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
            .contains('Next')
            .click();
    });

    it('Introduces the tasks', function() {
        cy.contains('This game switches between three tasks').should('be.visible');
        cy.contains('Digit Span').should('be.visible');
        cy.contains('Spatial Span').should('be.visible');
        cy.contains('Spatial Rotation').should('be.visible');

        cy.contains('Next')
            .should('be.visible')
            .click();
    });
});