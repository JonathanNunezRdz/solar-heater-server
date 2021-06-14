const router = require('express').Router();

router.get('/', async (req, res) => {
	try {
		// get data from mpu6050
		res.send({ xRotation: 12312.123, yRotation: 1231321.321 });
	} catch (error) {
		console.error(error);
		res.status(500).send(error);
	}
});
