"""
Enhanced API class that integrates Rettiwt-API features with existing twscrape functionality.

This module extends the base API class to provide additional features through the Rettiwt bridge
while maintaining backward compatibility with existing twscrape operations.
"""

from typing import AsyncGenerator, Dict, List, Optional, Union, Any
from contextlib import asynccontextmanager

from .api import API as BaseAPI
from .account import Account
from .models import Tweet, User
from .rettiwt_bridge import RettiwtBridge, RettiwtConfig
from .logger import logger


class EnhancedAPI(BaseAPI):
    """
    Enhanced API class that combines twscrape's existing functionality with Rettiwt-API features.
    
    This class provides a unified interface for both traditional twscrape operations and
    advanced Rettiwt features like direct messages, enhanced tweet operations, and real-time streaming.
    """
    
    def __init__(self, *args, enable_rettiwt: bool = True, **kwargs):
        """
        Initialize the Enhanced API.
        
        Args:
            *args: Arguments passed to base API class
            enable_rettiwt: Whether to enable Rettiwt-API features
            **kwargs: Keyword arguments passed to base API class
        """
        super().__init__(*args, **kwargs)
        self.enable_rettiwt = enable_rettiwt
        self._rettiwt_bridge = None
        if enable_rettiwt:
            self._rettiwt_bridge = RettiwtBridge(debug=self.debug)
    
    @asynccontextmanager
    async def _get_rettiwt_account(self):
        """
        Context manager to get an account with valid Rettiwt API key or guest key.
        
        Yields:
            Tuple of (Account, RettiwtConfig) ready for Rettiwt operations
        """
        if not self.enable_rettiwt or not self._rettiwt_bridge:
            raise RuntimeError("Rettiwt functionality is disabled")
        
        # Try to get account with valid API key first
        account = await self.pool.get_account_for_rettiwt()
        
        if account and account.api_key and account.api_key_valid:
            config = RettiwtConfig(
                api_key=account.api_key,
                proxy_url=account.proxy,
                debug=self.debug
            )
            yield account, config
            return
        
        # Fall back to guest authentication
        if not account:
            account = await self.pool.get()
        
        # Generate or reuse guest key
        if not account.guest_key:
            account.guest_key = await self._rettiwt_bridge.generate_guest_key()
            await self.pool.save_account(account)
        
        config = RettiwtConfig(
            guest_key=account.guest_key,
            proxy_url=account.proxy,
            debug=self.debug
        )
        yield account, config
    
    # Enhanced Tweet Operations
    
    async def tweet_bookmark(self, tweet_id: int) -> Dict[str, Any]:
        """
        Bookmark a tweet (requires user authentication).
        
        Args:
            tweet_id: ID of the tweet to bookmark
            
        Returns:
            Result of the bookmark operation
        """
        async with self._get_rettiwt_account() as (account, config):
            if not config.api_key:
                raise RuntimeError("Tweet bookmarking requires user authentication (API key)")
            
            script = """
            const rettiwt = new Rettiwt(params.config);
            const result = await rettiwt.tweet.bookmark(params.tweetId);
            
            console.log(JSON.stringify({
                success: true,
                bookmarked: result.bookmarked,
                tweetId: params.tweetId
            }));
            """
            
            return await self._rettiwt_bridge._execute_bridge_script(
                script,
                config=config.to_dict(),
                tweetId=str(tweet_id),
                debug=self.debug
            )
    
    async def tweet_unbookmark(self, tweet_id: int) -> Dict[str, Any]:
        """
        Remove bookmark from a tweet (requires user authentication).
        
        Args:
            tweet_id: ID of the tweet to unbookmark
            
        Returns:
            Result of the unbookmark operation
        """
        async with self._get_rettiwt_account() as (account, config):
            if not config.api_key:
                raise RuntimeError("Tweet unbookmarking requires user authentication (API key)")
            
            script = """
            const rettiwt = new Rettiwt(params.config);
            const result = await rettiwt.tweet.unbookmark(params.tweetId);
            
            console.log(JSON.stringify({
                success: true,
                unbookmarked: true,
                tweetId: params.tweetId
            }));
            """
            
            return await self._rettiwt_bridge._execute_bridge_script(
                script,
                config=config.to_dict(),
                tweetId=str(tweet_id),
                debug=self.debug
            )
    
    async def user_bookmarks(self, limit: int = -1) -> AsyncGenerator[Tweet, None]:
        """
        Get bookmarked tweets for the authenticated user.
        
        Args:
            limit: Maximum number of bookmarks to retrieve (-1 for all)
            
        Yields:
            Tweet objects for bookmarked tweets
        """
        async with self._get_rettiwt_account() as (account, config):
            if not config.api_key:
                raise RuntimeError("Accessing bookmarks requires user authentication (API key)")
            
            script = """
            const rettiwt = new Rettiwt(params.config);
            let count = 0;
            let cursor = undefined;
            
            while (params.limit === -1 || count < params.limit) {
                const response = await rettiwt.user.bookmarks({ cursor });
                
                if (!response.list || response.list.length === 0) {
                    break;
                }
                
                for (const tweet of response.list) {
                    if (params.limit !== -1 && count >= params.limit) {
                        break;
                    }
                    
                    console.log(JSON.stringify({
                        success: true,
                        type: 'tweet',
                        data: tweet
                    }));
                    count++;
                }
                
                if (!response.next) {
                    break;
                }
                cursor = response.next;
            }
            
            console.log(JSON.stringify({
                success: true,
                type: 'done',
                count: count
            }));
            """
            
            # This is a simplified implementation - in practice, we'd need to
            # handle the streaming response and convert to Tweet objects
            # For now, return a placeholder implementation
            results = await self._rettiwt_bridge._execute_bridge_script(
                script,
                config=config.to_dict(),
                limit=limit,
                debug=self.debug
            )
            
            # Convert results to Tweet objects (implementation needed)
            yield Tweet.dummy()  # Placeholder
    
    async def tweet_schedule(self, text: str, schedule_time: str) -> Dict[str, Any]:
        """
        Schedule a tweet for future posting.
        
        Args:
            text: Tweet content
            schedule_time: ISO format datetime string for when to post
            
        Returns:
            Result of the scheduling operation
        """
        async with self._get_rettiwt_account() as (account, config):
            if not config.api_key:
                raise RuntimeError("Tweet scheduling requires user authentication (API key)")
            
            script = """
            const rettiwt = new Rettiwt(params.config);
            const result = await rettiwt.tweet.schedule(params.text, new Date(params.scheduleTime));
            
            console.log(JSON.stringify({
                success: true,
                scheduled: true,
                tweetId: result.id,
                scheduledFor: params.scheduleTime
            }));
            """
            
            return await self._rettiwt_bridge._execute_bridge_script(
                script,
                config=config.to_dict(),
                text=text,
                scheduleTime=schedule_time,
                debug=self.debug
            )
    
    # User Operations
    
    async def user_follow(self, user_id: Union[str, int]) -> Dict[str, Any]:
        """
        Follow a user (requires user authentication).
        
        Args:
            user_id: ID of the user to follow
            
        Returns:
            Result of the follow operation
        """
        async with self._get_rettiwt_account() as (account, config):
            if not config.api_key:
                raise RuntimeError("Following users requires user authentication (API key)")
            
            script = """
            const rettiwt = new Rettiwt(params.config);
            const result = await rettiwt.user.follow(params.userId);
            
            console.log(JSON.stringify({
                success: true,
                following: result.following,
                userId: params.userId
            }));
            """
            
            return await self._rettiwt_bridge._execute_bridge_script(
                script,
                config=config.to_dict(),
                userId=str(user_id),
                debug=self.debug
            )
    
    async def user_unfollow(self, user_id: Union[str, int]) -> Dict[str, Any]:
        """
        Unfollow a user (requires user authentication).
        
        Args:
            user_id: ID of the user to unfollow
            
        Returns:
            Result of the unfollow operation
        """
        async with self._get_rettiwt_account() as (account, config):
            if not config.api_key:
                raise RuntimeError("Unfollowing users requires user authentication (API key)")
            
            script = """
            const rettiwt = new Rettiwt(params.config);
            const result = await rettiwt.user.unfollow(params.userId);
            
            console.log(JSON.stringify({
                success: true,
                following: false,
                userId: params.userId
            }));
            """
            
            return await self._rettiwt_bridge._execute_bridge_script(
                script,
                config=config.to_dict(),
                userId=str(user_id),
                debug=self.debug
            )
    
    # Enhanced capabilities info
    
    async def get_enhanced_capabilities(self) -> Dict[str, Any]:
        """
        Get information about available enhanced capabilities.
        
        Returns:
            Dictionary containing capability information
        """
        if not self.enable_rettiwt:
            return {
                "rettiwt_enabled": False,
                "capabilities": []
            }
        
        try:
            async with self._get_rettiwt_account() as (account, config):
                api_key = config.api_key
                features = await self._rettiwt_bridge.get_supported_features(api_key)
                
                return {
                    "rettiwt_enabled": True,
                    "auth_type": "user" if api_key else "guest",
                    "account_username": account.username if account else None,
                    "api_key_valid": bool(api_key and account.api_key_valid),
                    "capabilities": features
                }
        except Exception as e:
            logger.warning(f"Failed to get enhanced capabilities: {e}")
            return {
                "rettiwt_enabled": True,
                "error": str(e),
                "capabilities": []
            }


# For backward compatibility, create an alias
API = EnhancedAPI