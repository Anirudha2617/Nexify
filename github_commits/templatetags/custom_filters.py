# from django import template
# import json
# from  github_commits.models import Repository
# from django.shortcuts import render, redirect, get_object_or_404


# register = template.Library()

# @register.filter
# def dict_key(d, key):
#     """Access a dictionary's value by key in a Django template."""
#     try:
#         # print(d.get(key, '').answer_text)
#         return d.get(key, '')
    
#     except (AttributeError, TypeError):
#         return ''


# @register.filter
# def json_loads(value):
#     """Parses a JSON string into a Python object."""
#     try:
#         return json.loads(value)
#     except (json.JSONDecodeError, TypeError):
#         return []
    
# @register.filter
# def get_commits(value):
#     try:
#         return json.loads(value)
#     except (json.JSONDecodeError, TypeError):
#         return []

    
# @register.filter
# def get_repo(value):
#     return get_object_or_404(Repository, id = value)




# @register.simple_tag
# def process_answer(d, key , type = 'TEXT'):
#     """Access a dictionary's value by key in a Django template."""
#     try:
#         if type == 'LA' or type == 'DT' or  type == 'TEXT':
#             return d.get(key, '').answer_text
        
#         elif type == 'MC' or type == 'DD':
#             # print(d.get(key, '').answer_text.split(','))
#             return d.get(key, '').answer_text.split(',')
        
#         elif type == 'IMG':
#             return d.get(key, '').answer_image
        
#         elif type == 'JSON':
#             # print((d.get(key, '').json_answer))
#             return json.loads(d.get(key, '').json_answer)
        
#         elif type == 'GITHUB':
#             # ans  = d.get(key, '')
#             # ans.json_answer = json.loads(ans.json_answer)
#             # print("Printing repo name")
#             # print(ans.repo.name)
#             return json.loads(d.get(key, '').json_answer)
    
#     except (AttributeError, TypeError):
#         # print("Error")
#         return ''