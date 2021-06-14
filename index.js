const express = require('express');
const morgan = require('morgan');
const bodyParser = require('body-parser');
const mongoose = require('mongoose');
const cors = require('cors');
const { mongoURI } = require('./config/keys');

// import mongoDB models
require('./models');

const app = express();

app.use(morgan('common'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

app.use(
	cors({
		origin: (origin, callback) => {
			if (!origin) return callback(null, true);
			return callback(null, true);
		},
	})
);

app.all('*', (req, res, next) => {
	const origin = req.get('origin');
	res.header('Access-Control-Allow-Origin', origin);
	res.header('Access-Control-Allow-Headers', 'X-Requested-With');
	res.header('Access-Control-Allow-Headers', 'Content-Type');
	next();
});

// make app use routes
require('./routes')(app);

const PORT = process.env.PORT || 5000;

const connect = async () => {
	try {
		// setup gpio pins and mpu6050

		// apply acceleration calibration

		// connect to mongoose
		await mongoose.connect(mongoURI, {
			useNewUrlParser: true,
			useUnifiedTopology: true,
		});
		app.listen(PORT, () =>
			console.log(`solar=heater-server running on port: ${PORT}`)
		);
	} catch (error) {
		console.error(error);
	}
};

connect();
