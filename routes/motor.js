const router = require('express').Router();
const mongoose = require('mongoose');

const Motor = mongoose.model('motor');

// motor id 60c54ef7e817d131149e5f6b

router.get('/active', async (req, res) => {
	try {
		const dbMotor = await Motor.findById('60c54ef7e817d131149e5f6b');
		res.send(dbMotor);
	} catch (error) {
		console.error(error);
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
