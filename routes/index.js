const motor = require('./motor');

module.exports = (app) => {
	app.use('/api/motor', motor);
};
