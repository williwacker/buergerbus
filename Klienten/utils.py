from django.contrib import messages

def del_message(request):
	storage = messages.get_messages(request)
	for _ in storage:
		pass
	if len(storage._loaded_messages)  == 1:
		del storage._loaded_messages[0]