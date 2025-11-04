from .models import Tag

def popular_tags(request):
    try:
        popular_tags = Tag.objects.all().order_by('-usage_count')[:10]
        return {'popular_tags': popular_tags}
    except:
        # Если база данных еще не готова, возвращаем пустой список
        return {'popular_tags': []}
