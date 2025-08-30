// ***********************************************************
// This example support/e2e.ts is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import './commands'
import 'cypress-file-upload'

// cypress/support/e2e.js
before(() => {
  cy.request('GET', 'http://localhost:8000/health').its('status').should('eq', 200)
  cy.request('GET', 'http://localhost:3000').its('status').should('eq', 200)
});
