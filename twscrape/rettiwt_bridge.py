"""
Rettiwt-API bridge for integrating Node.js Rettiwt features into twscrape.

This module provides a Python interface to Rettiwt-API functionality through 
subprocess calls to Node.js, enabling advanced Twitter features while maintaining
twscrape's Python ecosystem.
"""

import asyncio
import json
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .logger import logger


class RettiwtBridge:
    """
    Bridge class for interfacing with Rettiwt-API from Python.
    
    This class manages Node.js subprocess calls to execute Rettiwt operations
    while maintaining async compatibility with twscrape's architecture.
    """
    
    def __init__(self, node_path: Optional[str] = None, debug: bool = False):
        """
        Initialize the Rettiwt bridge.
        
        Args:
            node_path: Path to Node.js executable. If None, uses system default.
            debug: Enable debug logging for bridge operations.
        """
        self.node_path = node_path or self._find_node()
        self.debug = debug
        self.bridge_dir = Path(__file__).parent / "rettiwt_bridge_scripts"
        self._ensure_bridge_scripts()
    
    def _find_node(self) -> str:
        """Find Node.js executable in system PATH."""
        try:
            result = subprocess.run(["which", "node"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        
        # Common paths for Node.js
        common_paths = [
            "/usr/local/bin/node",
            "/usr/bin/node", 
            "/opt/homebrew/bin/node",
            "node"  # fallback to PATH
        ]
        
        for path in common_paths:
            if os.path.exists(path) or path == "node":
                return path
        
        raise RuntimeError("Node.js not found in system. Please install Node.js or specify node_path.")
    
    def _ensure_bridge_scripts(self):
        """Ensure Node.js bridge scripts are available."""
        self.bridge_dir.mkdir(exist_ok=True)
        
        # Create package.json for the bridge scripts
        package_json = {
            "name": "twscrape-rettiwt-bridge",
            "version": "1.0.0",
            "type": "module",
            "dependencies": {
                "rettiwt-api": "^4.2.0"
            }
        }
        
        package_path = self.bridge_dir / "package.json"
        if not package_path.exists():
            with open(package_path, 'w') as f:
                json.dump(package_json, f, indent=2)
    
    async def ensure_dependencies(self):
        """Ensure Rettiwt-API dependencies are installed."""
        if not (self.bridge_dir / "node_modules").exists():
            logger.info("Installing Rettiwt-API dependencies...")
            process = await asyncio.create_subprocess_exec(
                "npm", "install",
                cwd=self.bridge_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown npm install error"
                raise RuntimeError(f"Failed to install Rettiwt-API: {error_msg}")
            
            logger.info("Rettiwt-API dependencies installed successfully")
    
    async def _execute_bridge_script(self, script_content: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a Node.js bridge script with given parameters.
        
        Args:
            script_content: JavaScript code to execute
            **kwargs: Parameters to pass to the script
            
        Returns:
            Dictionary containing the script execution result
        """
        await self.ensure_dependencies()
        
        # Create temporary script file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mjs', delete=False) as f:
            # Add imports and parameter injection
            full_script = f"""
import {{ Rettiwt }} from 'rettiwt-api';

// Parameters passed from Python
const params = {json.dumps(kwargs)};

// Utility function for logging
function log(message) {{
    if (params.debug) {{
        console.error(`[Rettiwt Bridge] ${{message}}`);
    }}
}}

// Main execution wrapper
async function main() {{
    try {{
        {script_content}
    }} catch (error) {{
        console.log(JSON.stringify({{
            success: false,
            error: error.message,
            stack: error.stack
        }}));
        process.exit(1);
    }}
}}

main();
"""
            f.write(full_script)
            script_path = f.name
        
        try:
            # Execute the script
            process = await asyncio.create_subprocess_exec(
                self.node_path, script_path,
                cwd=self.bridge_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if self.debug and stderr:
                logger.debug(f"Rettiwt bridge stderr: {stderr.decode()}")
            
            if process.returncode != 0:
                error_output = stderr.decode() if stderr else "Unknown error"
                raise RuntimeError(f"Rettiwt bridge script failed: {error_output}")
            
            # Parse JSON output
            try:
                result = json.loads(stdout.decode())
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse bridge script output: {stdout.decode()}")
                raise RuntimeError(f"Invalid JSON response from bridge script: {e}")
        
        finally:
            # Clean up temporary script
            try:
                os.unlink(script_path)
            except Exception:
                pass
    
    async def generate_guest_key(self) -> str:
        """
        Generate a guest authentication key for limited API access.
        
        Returns:
            Guest key string for Rettiwt authentication
        """
        script = """
        const rettiwt = new Rettiwt();
        const guestKey = await rettiwt.auth.guest();
        
        log(`Generated guest key: ${guestKey.substring(0, 10)}...`);
        
        console.log(JSON.stringify({
            success: true,
            guestKey: guestKey
        }));
        """
        
        result = await self._execute_bridge_script(script, debug=self.debug)
        if not result.get("success"):
            raise RuntimeError(f"Failed to generate guest key: {result.get('error')}")
        
        return result["guestKey"]
    
    async def validate_api_key(self, api_key: str) -> Dict[str, Any]:
        """
        Validate a Rettiwt API key and extract user information.
        
        Args:
            api_key: The API key to validate
            
        Returns:
            Dictionary containing validation result and user info
        """
        script = """
        try {
            const { AuthService } = await import('rettiwt-api');
            const userId = AuthService.getUserId(params.apiKey);
            const rettiwt = new Rettiwt({ apiKey: params.apiKey });
            
            // Try to fetch user details to validate the key
            const userDetails = await rettiwt.user.details({ id: userId });
            
            log(`API key validation successful for user: ${userDetails.username}`);
            
            console.log(JSON.stringify({
                success: true,
                valid: true,
                userId: userId,
                username: userDetails.username,
                userInfo: {
                    id: userDetails.id,
                    username: userDetails.username,
                    displayName: userDetails.fullName,
                    verified: userDetails.isVerified,
                    followersCount: userDetails.followersCount,
                    followingCount: userDetails.followingCount
                }
            }));
        } catch (error) {
            log(`API key validation failed: ${error.message}`);
            console.log(JSON.stringify({
                success: true,
                valid: false,
                error: error.message
            }));
        }
        """
        
        return await self._execute_bridge_script(script, apiKey=api_key, debug=self.debug)
    
    async def get_supported_features(self, api_key: Optional[str] = None) -> List[str]:
        """
        Get list of supported Rettiwt features based on authentication type.
        
        Args:
            api_key: Optional API key. If None, returns guest features only.
            
        Returns:
            List of supported feature names
        """
        script = """
        const authType = params.apiKey ? 'user' : 'guest';
        
        const guestFeatures = [
            'tweet_details',
            'user_details_by_username', 
            'user_replies_timeline',
            'user_timeline'
        ];
        
        const userFeatures = [
            ...guestFeatures,
            'list_tweets',
            'list_members', 
            'tweet_like',
            'tweet_media_upload',
            'tweet_post',
            'tweet_retweet',
            'tweet_retweeters',
            'tweet_schedule',
            'tweet_search',
            'tweet_stream',
            'tweet_unlike',
            'tweet_unpost',
            'tweet_unretweet',
            'user_bookmarks',
            'user_details_by_id',
            'user_follow',
            'user_followed_feed',
            'user_followers',
            'user_following',
            'user_highlights',
            'user_likes',
            'user_media',
            'user_notifications',
            'user_recommended_feed',
            'user_subscriptions',
            'user_unfollow'
        ];
        
        const features = authType === 'user' ? userFeatures : guestFeatures;
        
        log(`Available ${authType} features: ${features.length}`);
        
        console.log(JSON.stringify({
            success: true,
            authType: authType,
            features: features
        }));
        """
        
        result = await self._execute_bridge_script(script, apiKey=api_key, debug=self.debug)
        if not result.get("success"):
            raise RuntimeError(f"Failed to get supported features: {result.get('error')}")
        
        return result["features"]


class RettiwtConfig:
    """Configuration class for Rettiwt bridge settings."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        guest_key: Optional[str] = None,
        proxy_url: Optional[str] = None,
        debug: bool = False
    ):
        self.api_key = api_key
        self.guest_key = guest_key
        self.proxy_url = proxy_url
        self.debug = debug
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for JSON serialization."""
        config = {}
        if self.api_key:
            config["apiKey"] = self.api_key
        if self.guest_key:
            config["guestKey"] = self.guest_key
        if self.proxy_url:
            config["proxyUrl"] = self.proxy_url
        if self.debug:
            config["logging"] = True
        return config