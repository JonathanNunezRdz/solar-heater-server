const chalk = require('chalk');

const errorC = chalk.red;
const warningC = chalk.yellow;
const successC = chalk.green;

const log = console.log;
const logError = (msg) => console.error(errorC(msg));

const sleep = (ms) => new Promise((res) => setTimeout(res, ms));

module.exports = {
	errorC,
	warningC,
	successC,
	log,
	logError,
	sleep,
};
