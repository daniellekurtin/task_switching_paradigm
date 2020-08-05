/*
To run the test we use `npm run ci`
 */

describe("Task switching paradigm (JS)", function () {

    it('Welcomes the user', function () {
        cy.visit('localhost:8080');

        cy.get('strong')
            .should('be.visible')
            .contains('Task Switching Game');

        cy.get('#jspsych-instructions-next')
            .should('be.visible')
            .click()
    });
});