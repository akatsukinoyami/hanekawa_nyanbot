from words.ru.nyan import nyan as ru_nyan
from words.ru.lewd import lewd as ru_lewd
from words.ru.angr import angr as ru_angr
from words.ru.scar import scar as ru_scar

from words.en.nyan import nyan as en_nyan
from words.en.lewd import lewd as en_lewd
from words.en.angr import angr as en_angr
from words.en.scar import scar as en_scar

reacts = {
	'ru': {
		'nyan':ru_nyan,
		'lewd':ru_lewd,
		'angr':ru_angr,
		'scar':ru_scar,
	},
	'en': {
		'nyan':en_nyan,
		'lewd':en_lewd,
		'angr':en_angr,
		'scar':en_scar,
	}
}