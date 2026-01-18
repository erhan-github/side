#!/usr/bin/env node

const inquirer = require('inquirer');
const chalk = require('chalk');
const ora = require('ora');
const fs = require('fs-extra');
const path = require('path');
const os = require('os');
const { execSync } = require('child_process');

async function main() {
    console.log(chalk.bold.white('\n🧠 CSO.ai | Your Strategic Partner\n'));

    // 1. Detect Environment
    const questions = [
        {
            type: 'list',
            name: 'editor',
            message: 'Where do you want to install Intelligence?',
            choices: ['Cursor', 'VS Code'],
            default: 'Cursor'
        },
        {
            type: 'input',
            name: 'projectPath',
            message: 'Path to your project (where .cso folder will live):',
            default: process.cwd()
        }
    ];

    const answers = await inquirer.prompt(questions);
    const editor = answers.editor;
    const projectPath = path.resolve(answers.projectPath);

    const spinner = ora('Analyzing neural pathways...').start();
    await new Promise(resolve => setTimeout(resolve, 800)); // Fake think time

    try {
        // 2. Locate Settings File based on OS and Editor
        let settingsPath;
        const platform = os.platform();
        const home = os.homedir();

        if (platform === 'darwin') { // macOS
            if (editor === 'Cursor') {
                settingsPath = path.join(home, 'Library/Application Support/Cursor/User/settings.json');
            } else {
                settingsPath = path.join(home, 'Library/Application Support/Code/User/settings.json');
            }
        } else {
            // Fallback for other OSs (implied TODO)
            // Check Windows/Linux paths if needed, for MVP we focus on Mac as per user OS
            if (editor === 'Cursor') {
                // Windows: %APPDATA%\Cursor\User\settings.json
                // Linux: ~/.config/Cursor/User/settings.json
                settingsPath = path.join(home, '.config/Cursor/User/settings.json'); // Linux assumption
            } else {
                settingsPath = path.join(home, '.config/Code/User/settings.json');
            }
        }

        // 3. Prepare MCP Config
        // We assume the python package is installed via pip or uv
        // For this installer, we will point to the `uvx` or `python` command
        const mcpConfig = {
            "side-mcp": {
                "command": "uvx",
                "args": [
                    "side-mcp"
                ]
            }
        };

        spinner.text = `Injecting intelligence into ${editor}...`;

        // 4. Read & Update Settings
        if (await fs.pathExists(settingsPath)) {
            const settings = await fs.readJson(settingsPath);

            // Ensure mcpServers object exists
            if (!settings['mcpServers']) {
                settings['mcpServers'] = {};
            }

            // Inject Config
            settings['mcpServers'] = {
                ...settings['mcpServers'],
                ...mcpConfig
            };

            await fs.writeJson(settingsPath, settings, { spaces: 4 });
            spinner.succeed(chalk.green('Intelligence Injected Successfully.'));
        } else {
            spinner.fail(chalk.red(`Could not find ${editor} settings at ${settingsPath}`));
            console.log(chalk.yellow('Please manually add the following to your settings.json:'));
            console.log(JSON.stringify(mcpConfig, null, 2));
        }

        // 5. Final Success Message
        console.log('\n' + chalk.bold.blue('Next Steps:'));
        console.log('1. Restart ' + editor);
        console.log('2. Open the AI Pane');
        console.log('3. Type: "Plan my next feature"');
        console.log('\n' + chalk.dim('Strategic Token Balance: 0 (Refill at CSO.ai)'));

    } catch (error) {
        spinner.fail('Installation failed.');
        console.error(error);
    }
}

main();
