import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    let disposable = vscode.commands.registerCommand('mini-github-copilot.askCode', async () => {
        try {
            // Use dynamic import for node-fetch
            const fetch = (await import('node-fetch')).default;
            const res = await fetch('http://localhost:8000/dummy');
            if (!res.ok) throw new Error('Network response was not ok');
            const data = await res.json() as { message?: string };
            vscode.window.showInformationMessage('Backend response: ' + (data.message ?? 'No message'));
        } catch (error) {
            vscode.window.showErrorMessage('Failed to connect to backend: ' + error);
        }
    });
    context.subscriptions.push(disposable);
}

export function deactivate() {}
