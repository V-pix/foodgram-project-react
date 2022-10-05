import random

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from users.models import CustomUser


def confirmation_generator(username):
    """Generate confirmation codes"""

    user = get_object_or_404(CustomUser, username=username)
    confirmation_code = "".join([random.choice(settings.CONF_GEN) for x in range(15)])
    user.confirmation_code = confirmation_code
    user.save()

    send_mail(
        settings.MAIL_SUBJECT,
        confirmation_code,
        settings.FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


@action(detail=False, methods=["GET"], url_path="download_shopping_cart")
    def download_shopping_cart(self, request):
        shopping_list = {}
        ingredients = RecipeIngredients.objects.filter(
            recipe__carts__user=request.user
        ).annotate(sum('amount'))
        ingredients = RecipeIngredients.objects.filter(
            recipe__carts__user=request.user).values(
                'ingredient__name',
                'ingredient__measurement_unit'
        ).annotate(sum('amount'))
        for ingredient in ingredients:
            amount = ingredient.total
            name = ingredient.ingredient.name
            measurement_unit = ingredient.ingredient.measurement_unit
            shopping_list[name] = {
                'measurement_unit': measurement_unit,
                'amount': amount
            }
        main_list = ([f"{item}: {value['amount']}"
                      f" {value['measurement_unit']}\n"
                      for item, value in shopping_list.items()])
        response = HttpResponse(main_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="Cart.txt"'
        return response
        
    @action(detail=False, methods=["GET"], url_path="download_shopping_cart123")
    def download_shopping_cart123(self, request):
        ingredients = RecipeIngredients.objects.filter(
            recipe__shoppingcart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(sum('amount'))
        # shopping_list = create_shopping_list(ingredients)
        response = HttpResponse(
            # shopping_list,
            content_type='text/plain')
        response['Content-Disposition'] = ('attachment; filename="ShoppingCart.txt"')
        return response
        # return FileResponse(
        #     shopping_list,
        #     as_attachment=True,
        #     filename='shopping_list.pdf'
        # )
    
    @# action(detail=False, methods=["GET"], url_path="download_shopping_cart123")
    def get_download_shopping_cart123(self, request):
        # buf = io.BytesIO()
        can = canvas.Canvas(buf, pagesize=letter, bottomup=0)
        textob = can.beginText()
        textob.setTextOrigin(inch, inch)
        textob.setFont("Halventica", 14)
        
        contex=ShoppingCart.objects.all()
        
        lines=[]
        
        for con in contex:
            lines.append(con.recipe)
            lines.append(' ')
        
        for line in lines:
            textob.textLine(line)
            
        can.drawText(textob)
        can.showPage()
        can.save()
        buf.seek(0)
        
        return FileResponse(buf, as_attachment=True, filename="shopping_cart.pdf")
        