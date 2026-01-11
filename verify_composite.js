const https = require('https');

const MCP_SERVER_URL = 'https://mcp-server-production-abe0.up.railway.app/tools/call';

async function callTool(name, args) {
    return new Promise((resolve, reject) => {
        const data = JSON.stringify({ name, arguments: args });
        const url = new URL(MCP_SERVER_URL);
        const options = {
            hostname: url.hostname,
            path: url.pathname,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': data.length
            }
        };

        const req = https.request(options, (res) => {
            let body = '';
            res.on('data', (chunk) => body += chunk);
            res.on('end', () => {
                try {
                    if (res.statusCode >= 200 && res.statusCode < 300) {
                        const response = JSON.parse(body);
                        if (response.content && response.content[0] && response.content[0].text) {
                            resolve(JSON.parse(response.content[0].text));
                        } else {
                            resolve(response);
                        }
                    } else {
                        reject(new Error(`Status ${res.statusCode}: ${body}`));
                    }
                } catch (e) {
                    reject(e);
                }
            });
        });

        req.on('error', (e) => reject(e));
        req.write(data);
        req.end();
    });
}

async function main() {
    try {
        console.log('--- Deep Verification for "Composite" ---');

        // Search 1: Broad search for "composite" to see all contexts
        console.log('\n[Broad Search: "composite"]');
        const searchComposite = await callTool('search_corpus', { query: 'composite', limit: 30 });

        if (searchComposite.results) {
            console.log(`Found ${searchComposite.count} results.`);
            searchComposite.results.forEach((res, i) => {
                if (res.text && (res.text.toLowerCase().includes('power') || res.text.toLowerCase().includes('strength'))) {
                    console.log(`\n[POTENTIAL MATCH #${i + 1}]`);
                    console.log(`President: ${res.president}`);
                    console.log(`Date: ${res.date}`);
                    console.log(`Snippet: ${res.text}`);
                }
            });
            // print first few regardless of match to check word usage
            searchComposite.results.slice(0, 5).forEach((res, i) => {
                console.log(`\n[Sample #${i + 1}] ${res.text.substring(0, 150)}...`);
            });
        }

        // Search 2: "composite strength"
        console.log('\n[Phrase Search: "composite strength"]');
        const phraseStrength = await callTool('search_phrases', { phrase: 'composite strength', limit: 10 });
        console.log(JSON.stringify(phraseStrength, null, 2));

    } catch (error) {
        console.error('Error:', error);
    }
}

main();
