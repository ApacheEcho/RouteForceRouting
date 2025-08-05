/**
 * Test file to validate CodeQL analysis setup for JavaScript/TypeScript.
 * This file contains intentional security issues that CodeQL should detect.
 */

// This should trigger CodeQL's XSS detection
function potentialXSS(userInput: string): void {
    // Intentionally vulnerable code - CodeQL should flag this
    document.getElementById('output')!.innerHTML = userInput;
}

// This should trigger CodeQL's prototype pollution detection
function potentialPrototypePollution(obj: any, key: string, value: any): void {
    // Intentionally vulnerable code - CodeQL should flag this
    obj[key] = value;
}

// This should trigger CodeQL's hardcoded credentials detection
function hardcodedSecret(): string {
    // Intentionally vulnerable code - CodeQL should flag this
    const apiKey = "sk-1234567890abcdef";
    return apiKey;
}

// This should trigger CodeQL's unsafe eval detection
function potentialCodeInjection(userCode: string): any {
    // Intentionally vulnerable code - CodeQL should flag this
    return eval(userCode);
}

console.log('CodeQL TypeScript test file created - contains intentional security issues for testing');
console.log('CodeQL should detect:');
console.log('1. XSS in potentialXSS()');
console.log('2. Prototype pollution in potentialPrototypePollution()');
console.log('3. Hardcoded credentials in hardcodedSecret()');
console.log('4. Code injection in potentialCodeInjection()');

export { potentialXSS, potentialPrototypePollution, hardcodedSecret, potentialCodeInjection };