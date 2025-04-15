import sys
import os


def convert_to_django_template(template_path, static_path):
    try:
        with open(template_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Add Django static tag at the beginning if not present
        if "{% load static %}" not in content:
            content = "{% load static %}\n" + content

        # Convert various static file references
        replacements = [
            ('src="../assets/', 'src="{% static \'advadmin/assets/'),
            ('href="../assets/', 'href="{% static \'advadmin/assets/'),
            ('url(../assets/', 'url({% static \'advadmin/assets/'),
            ('data-app-dark-img="../assets/', 'data-app-dark-img="{% static \'advadmin/'),
            ('data-app-light-img="../assets/', 'data-app-light-img="{% static \'advadmin/')
        ]

        for old, new in replacements:
            content = content.replace(old, new)

        # Close the static tags properly
        content = content.replace('.css"', '.css\' %}"')
        content = content.replace('.js"', '.js\' %}"')
        content = content.replace('.png"', '.png\' %}"')
        content = content.replace('.jpg"', '.jpg\' %}"')
        content = content.replace('.jpeg"', '.jpeg\' %}"')
        content = content.replace('.gif"', '.gif\' %}"')
        content = content.replace('.ico"', '.ico\' %}"')
        content = content.replace('.svg"', '.svg\' %}"')
        content = content.replace('.woff"', '.woff\' %}"')
        content = content.replace('.woff2"', '.woff2\' %}"')

        # Handle cases where the path might end with a quote or other characters
        content = content.replace("')", "' %})")
        content = content.replace('")', "' %})")

        # Save the modified file
        with open(template_path, "w", encoding="utf-8") as file:
            file.write(content)

        print(f"Successfully converted {template_path} to a Django template.")
        return True
    except Exception as e:
        print(f"Error converting {template_path}: {str(e)}")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python STMAKER.py <template_path <static_path")
        print("Example: python STMAKER.py templates/index.html static/")
    else:
        template_path = sys.argv[1]
        static_path = sys.argv[2]
        
        if not os.path.exists(template_path):
            print(f"Error: Template file not found at {template_path}")
        else:
            success = convert_to_django_template(template_path, static_path)
            if not success:
                sys.exit(1)



#  python STMAKER.py "C:\Users\Appz\Desktop\CSSBASE\cssbase\templates\advadmin\auth-forgot-password-basic.html" "C:\Users\Appz\Desktop\CSSBASE\cssbase\static\advadmin"


# python STMAKER.py "C:\Users\Appz\Desktop\CSSBASE\cssbase\templates\advadmin\pages-account-settings-account.html" "C:\Users\Appz\Desktop\CSSBASE\cssbase\static\advadmin"