const mongoose = require('mongoose');
const { Schema } = mongoose;

const motorSchema = new Schema({
	name: String,
	active: Boolean,
	direction: String,
});

mongoose.model('motor', motorSchema);
