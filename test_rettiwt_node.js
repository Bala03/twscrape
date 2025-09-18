#!/usr/bin/env node

/**
 * Test script to verify Rettiwt-API functionality
 */

async function testRettiwtBasic() {
    console.log("=== Testing Rettiwt-API Installation ===");
    
    try {
        // Test if we can import Rettiwt
        const RettiwtPackage = await import('rettiwt-api');
        console.log("✓ Rettiwt-API imported successfully");
        console.log("Available exports:", Object.keys(RettiwtPackage));
        
        const { Rettiwt } = RettiwtPackage;
        
        // Test creating instance
        const rettiwt = new Rettiwt();
        console.log("✓ Rettiwt instance created");
        console.log("Instance methods:", Object.getOwnPropertyNames(Object.getPrototypeOf(rettiwt)));
        
        // Test static methods
        try {
            // Check if AuthService is available as a static method
            if (Rettiwt.AuthService) {
                const testCookie = "test=value";
                const encoded = Rettiwt.AuthService.encodeCookie(testCookie);
                const decoded = Rettiwt.AuthService.decodeCookie(encoded);
                console.log("✓ Cookie encoding/decoding works");
            } else {
                console.log("? Cookie methods not accessible as static methods");
            }
        } catch (e) {
            console.log("✗ Cookie methods failed:", e.message);
        }
        
        // Test guest key generation
        try {
            console.log("Generating guest key...");
            const guestKey = await rettiwt.auth.guest();
            console.log(`✓ Guest key generated: ${guestKey.substring(0, 20)}...`);
        } catch (e) {
            console.log("✗ Guest key generation failed:", e.message);
        }
        
        console.log("\n=== Rettiwt-API Test Completed ===");
        return true;
        
    } catch (error) {
        console.log("✗ Rettiwt-API test failed:", error.message);
        console.log("\nTrying to install Rettiwt-API...");
        
        // Try to install the package
        const { spawn } = require('child_process');
        const npm = spawn('npm', ['install', 'rettiwt-api'], { stdio: 'inherit' });
        
        return new Promise((resolve, reject) => {
            npm.on('close', (code) => {
                if (code === 0) {
                    console.log("✓ Rettiwt-API installed successfully");
                    resolve(true);
                } else {
                    console.log("✗ Failed to install Rettiwt-API");
                    resolve(false);
                }
            });
        });
    }
}

// Run the test
testRettiwtBasic()
    .then(success => {
        process.exit(success ? 0 : 1);
    })
    .catch(error => {
        console.error("Test failed:", error);
        process.exit(1);
    });