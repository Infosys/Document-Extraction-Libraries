# Infy Search Service Tool

This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 17.0.5.

## Installation

To install node_modules run the command `pnpm install` in the root directory of the project.
Make sure to have pnpm intalled in your machine. If not, you can install it by running `npm install -g pnpm@8.5.1`.

## Pre-requisites

**1.Search service:**
Make sure to have an instance of search service running in you local machine. The application points to the search service running in `http://localhost:8003`. If you have the search service running in a different port, instance kindly make necessary changes in the service file `src/app/services/search.service.ts`.

**2.VectorDB:**
Make sure according to your search service configurations and setup, you have a valid vector database at the correct path.

## Development server

Run `npm run start` for a dev server. Navigate to `http://localhost:4200/`. The application will automatically reload if you change any of the source files.

## Code scaffolding

Run `ng generate component component-name` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

## Build

Run `npm run build` to build the project. The build artifacts will be stored in the `dist/` directory.

## Running unit tests

Run `npm run test` to execute the unit tests via [Karma](https://karma-runner.github.io).

## Running end-to-end tests

Run `ng e2e` to execute the end-to-end tests via a platform of your choice. To use this command, you need to first add a package that implements end-to-end testing capabilities.

## Further help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI Overview and Command Reference](https://angular.io/cli) page.
