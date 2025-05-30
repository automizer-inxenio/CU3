from homeassistant import config_entries
import voluptuous as vol
class AutomizerOptionsFlowHandler(config_entries.OptionsFlow):
	def __init__(A,config_entry):A.config_entry=config_entry
	async def async_step_init(A,user_input=None):
		D='port';C='host';B=user_input
		if B is not None:return A.async_create_entry(title='',data=B)
		return A.async_show_form(step_id='init',data_schema=vol.Schema({vol.Required(C,default=A.config_entry.data.get(C,'')):str,vol.Required(D,default=A.config_entry.data.get(D,1234)):int}))