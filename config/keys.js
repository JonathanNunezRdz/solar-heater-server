if (process.env.NODE_ENV === 'production') {
	const keys = {
		mongoURI: process.env.MONGO_URI,
	};
	module.exports = keys;
} else module.exports = require('./dev');
