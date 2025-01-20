from django import template
import json
from  github_commits.models import Repository
from django.shortcuts import render, redirect, get_object_or_404

register = template.Library()

@register.filter
def dict_key(d, key):
    """Access a dictionary's value by key in a Django template."""
    try:
        return d.get(key, '')
    
    except (AttributeError, TypeError):
        return ''


@register.filter
def json_loads(value):
    """Parses a JSON string into a Python object."""
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return []
    
@register.filter
def get_commits(repo_id):
    repo = get_object_or_404(Repository, id = repo_id)
    return repo.commits.all()

@register.filter
def get_repo(value):
    return get_object_or_404(Repository, id = value)



@register.simple_tag
def process_answer(d, key , type = 'TEXT'):
    """Access a dictionary's value by key in a Django template."""
    try:
        if type == 'LA' or type == 'DT' or  type == 'TEXT':
            return d.get(key, '').answer_text
        
        elif type == 'MC' or type == 'DD':
            # print(d.get(key, '').answer_text.split(','))
            return d.get(key, '').answer_text.split(',')
        
        elif type == 'IMG':
            return d.get(key, '').answer_image
        
        elif type == 'JSON':
            # print((d.get(key, '').json_answer))
            return json.loads(d.get(key, '').json_answer)
        
        elif type == 'GITHUB':
            json_data = d.get(key)
            if not json_data:
                raise ValueError("Key not found in the dictionary.")
            answer = {}
            op = json.loads(json_data.json_answer)

            # answer['repo'] = get_object_or_404(Repository, id=op['repo_id'])
            try:
                answer['repo'] = Repository.objects.filter(id = op['repo_id'])[0]
                print(answer['repo'])
                answer['branches'] = answer['repo'].branches.filter(id__in=op['branch_list'])
                answer['username'] = op['username']
            except:
                pass
            return answer

    
    except (AttributeError, TypeError):
        # print("Error")
        return ''