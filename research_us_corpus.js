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
                        // MCP returns { content: [{ type: 'text', text: JSONString }] }
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
        console.log('--- Dictionary Research ---');

        console.log('\n[Defining "comprehensive" in Chambers]');
        const compChambers = await callTool('define_word', { word: 'comprehensive', type: 'chambers' });
        console.log(JSON.stringify(compChambers, null, 2));

        console.log('\n[Defining "composite" in Chambers]');
        const compositeChambers = await callTool('define_word', { word: 'composite', type: 'chambers' });
        console.log(JSON.stringify(compositeChambers, null, 2));

        console.log('\n[The Right Word: "comprehensive"]');
        const rightWord = await callTool('define_word', { word: 'comprehensive', type: 'rightword' });
        console.log(JSON.stringify(rightWord, null, 2));

        console.log('\n--- US Presidential Corpus Research ---');

        console.log('\n[Searching phrase "comprehensive power"]');
        const searchComp = await callTool('search_phrases', { phrase: 'comprehensive power', limit: 10 });
        console.log(JSON.stringify(searchComp, null, 2));

        console.log('\n[Searching phrase "composite power"]');
        const searchComposite = await callTool('search_phrases', { phrase: 'composite power', limit: 10 });
        console.log(JSON.stringify(searchComposite, null, 2));

        console.log('\n[Searching phrase "national power"]');
        const searchNational = await callTool('search_phrases', { phrase: 'national power', limit: 10 });
        console.log(JSON.stringify(searchNational, null, 2));

        console.log('\n[Searching phrase "aggregate power"]');
        const searchAggregate = await callTool('search_phrases', { phrase: 'aggregate power', limit: 10 });
        console.log(JSON.stringify(searchAggregate, null, 2));

        console.log('\n[EC Dict Lookup: "comprehensive national power"]');
        const ecDict = await callTool('define_word', { word: 'comprehensive national power', type: 'ec_dict' });
        console.log(JSON.stringify(ecDict, null, 2));

    } catch (error) {
        console.error('Error:', error);
    }
}

main();
