const router = require('express').Router();
const mongoose = require('mongoose');
const { sleep, logError, log, errorC } = require('../utils');

const Motor = mongoose.model('motor');

// motor id 60c54ef7e817d131149e5f6b

router.put('activate', async (req, res) => {
	try {
		const { active } = req.body;
		let dbMotor = await Motor.findById('60c54ef7e817d131149e5f6b');
		if (dbMotor.active === active) {
			const message = `Motor is already ${active ? 'on' : 'off'}`;
			log(errorC(message));
			return res.status(409).send({ message });
		}

		// turn motor on with gpio

		dbMotor.active = active;
		dbMotor = await dbMotor.save();

		res.send(dbMotor);
	} catch (error) {
		logError(error);
		res.status(500).send(error);
	}
});

router.put('toggle_motor_duration', async (req, res) => {
	try {
		let dbMotor = await Motor.findById('60c54ef7e817d131149e5f6b');
		if (dbMotor.active) {
			const message = `Can't toggle motor when it's on.`;
			log(errorC(message));
			return res.status(409).send({ message });
		}

		const { duration } = req.body;
		dbMotor.active = true;
		dbMotor = await dbMotor.save();

		// toggle motor for x duration with gpio
		// turn on motor
		await sleep(Number(duration) * 1000);
		// turn off motor

		dbMotor.active = false;
		dbMotor = await dbMotor.save();

		res.send({ duration: Number(duration) });
	} catch (error) {
		logError(error);
		res.status(500).send(error);
	}
});

router.get('/active', async (req, res) => {
	try {
		const dbMotor = await Motor.findById('60c54ef7e817d131149e5f6b');
		res.send(dbMotor);
	} catch (error) {
		logError(error);
		res.status(500).send(error);
	}
});

// router.put('/active', async (req, res) => {
//     try {
//         const { active } = req.body;
//         const dbMotor = await Motor.find
//     } catch (error) {

//     }
// })

// router.post('/init', async (req, res) => {
// 	try {
// 		const dbMotor = await new Motor({
// 			name: 'c2',
// 			active: false,
// 			direction: 'up',
// 		}).save();
// 		console.log(dbMotor);
// 		res.sendStatus(200);
// 	} catch (error) {
// 		res.status(500).send(error);
// 	}
// });

module.exports = router;
