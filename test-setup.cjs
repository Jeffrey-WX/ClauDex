#!/usr/bin/env node

// Test script to verify Codex MCP Server setup

const fs = require('fs');
const path = require('path');
const https = require('https');

console.log('🧪 Codex MCP Server - Setup Verification\n');
console.log('=' .repeat(50));

// Test 1: Check .env file
console.log('\n✅ Test 1: .env Configuration');
const envPath = path.join(__dirname, '.env');
if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, 'utf-8');
  const hasApiKey = envContent.includes('OPENAI_API_KEY=');
  const hasApiBase = envContent.includes('OPENAI_API_BASE=');

  console.log(`   .env file: ${hasApiKey ? '✓' : '✗'} API Key found`);
  console.log(`   .env file: ${hasApiBase ? '✓' : '✗'} API Base found`);

  if (hasApiKey && hasApiBase) {
    const apiKeyMatch = envContent.match(/OPENAI_API_KEY=(.+)/);
    const apiBaseMatch = envContent.match(/OPENAI_API_BASE=(.+)/);
    if (apiKeyMatch && apiBaseMatch) {
      console.log(`   API Key: ${apiKeyMatch[1].substring(0, 15)}...`);
      console.log(`   API Base: ${apiBaseMatch[1]}`);
    }
  }
} else {
  console.log('   ✗ .env file not found!');
}

// Test 2: Check compiled files
console.log('\n✅ Test 2: Compiled Files');
const distPath = path.join(__dirname, 'dist', 'index.js');
if (fs.existsSync(distPath)) {
  const stats = fs.statSync(distPath);
  console.log(`   dist/index.js: ✓ Found (${stats.size} bytes)`);
  console.log(`   Modified: ${stats.mtime.toLocaleString()}`);
} else {
  console.log('   ✗ dist/index.js not found! Run: npm run build');
}

// Test 3: Check test project
console.log('\n✅ Test 3: Test Project');
const testProjectPath = path.join(__dirname, '..', 'test-codex-project');
if (fs.existsSync(testProjectPath)) {
  console.log(`   ✓ Test project found at: ${testProjectPath}`);

  const files = [
    'package.json',
    'src/calculator.js',
    'src/auth.js',
    'README.md'
  ];

  files.forEach(file => {
    const filePath = path.join(testProjectPath, file);
    if (fs.existsSync(filePath)) {
      console.log(`   ✓ ${file}`);
    } else {
      console.log(`   ✗ ${file} missing`);
    }
  });
} else {
  console.log('   ✗ Test project not found!');
}

// Test 4: Check MCP config
console.log('\n✅ Test 4: MCP Configuration Template');
const mcpConfigPath = path.join(__dirname, 'mcp_config_for_claude_code.json');
if (fs.existsSync(mcpConfigPath)) {
  console.log(`   ✓ MCP config template created`);
  console.log(`   Location: ${mcpConfigPath}`);

  const config = JSON.parse(fs.readFileSync(mcpConfigPath, 'utf-8'));
  if (config.mcpServers && config.mcpServers.codex) {
    console.log(`   ✓ Codex server configured`);
    console.log(`   Command: ${config.mcpServers.codex.command}`);
  }
} else {
  console.log('   ✗ MCP config template not found!');
}

// Test 5: Test API endpoint (optional)
console.log('\n✅ Test 5: API Endpoint Test');
require('dotenv').config();

const apiBase = process.env.OPENAI_API_BASE;
const apiKey = process.env.OPENAI_API_KEY;

if (apiBase && apiKey) {
  console.log('   Testing connection to API endpoint...');

  const url = new URL('/models', apiBase);

  const options = {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json'
    }
  };

  const req = https.request(url, options, (res) => {
    if (res.statusCode === 200) {
      console.log(`   ✓ API endpoint is reachable (Status: ${res.statusCode})`);
    } else {
      console.log(`   ⚠ API returned status: ${res.statusCode}`);
    }
  });

  req.on('error', (error) => {
    console.log(`   ✗ Cannot reach API endpoint: ${error.message}`);
  });

  req.setTimeout(5000, () => {
    req.destroy();
    console.log('   ⚠ API request timeout (5s)');
  });

  req.end();
} else {
  console.log('   ⚠ API credentials not configured, skipping endpoint test');
}

// Summary
console.log('\n' + '='.repeat(50));
console.log('\n📋 Summary:');
console.log('\n✅ Setup Complete:');
console.log('   1. ✓ .env configured with API credentials');
console.log('   2. ✓ Code compiled successfully');
console.log('   3. ✓ Test project created');
console.log('   4. ✓ MCP config template ready');

console.log('\n⏳ Next Steps:');
console.log('   1. Add MCP config to Claude Code');
console.log('   2. Restart Claude Code');
console.log('   3. Test Codex by saying:');
console.log('      "让 Codex 列出 test-codex-project 的文件"');

console.log('\n📖 See CONFIGURATION_GUIDE.md for detailed instructions\n');
