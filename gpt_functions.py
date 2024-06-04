import os
import pandas as pd
import json5
import openai
import json
from dotenv import load_dotenv
load_dotenv()

comments_no_default = {
  "order": {
    "order_info": {
      "description": "Order form key: Omschrijving",
      "reference": "Order form key: Nr.",
      "type": "Lithograaf archiefnr. Ingevulde waarde zichtbaar = Wijziging/Repeat, niet zichtbaar = Nieuw"
    },
    "items": {
      "item": {
        "measurements": {
          "label_width": "Order form key: Netto foliebreedte (mm)",
          "label_height": "Order form key: Slaglengte (mm)",
          "amount_horizontal_labels": "Order form key: Aantal banen",
          "amount_vertical_labels": "Order form key calculate: Cilinderomvang (mm) divided by Slaglengte (mm), rounded down",
          "width_and_horizontal_gap": "Order form key: Netto foliebreedte",
          "height_and_vertical_gap": "Order form key calculate: Cilinderomvang (mm) / amount_vertical_labels",
        },
        "printer": {
          "plate_type": "Mag voor Altacel van Kodak NX 1 naar Kodak NX 1.14 worden geconverteerd. Plaattype is ook uit het Kleurprofiel te halen (uit de email)",
          "side": "Order form key: Bedrukking",
        },
        "printerspecs": {
          "cylinder_circumference": "Order form key: Cilinderomvang (mm)",
          "material_width": "Order form: Bruto foliebreedte (mm)",
          "roll_winding": "Order form key: Eindwikkeling",
        },
        "plates": {
          "plate": {
            "color": [
              {
                "name": "Order form: Retrieve from Table1, IF PMS PRESENT: USE PMS ELSE: COLOR NAME[x]/Kleurnaam[x]",
              },
              {
                "name": "Order form: Retrieve from Table1, IF PMS PRESENT: USE PMS ELSE: COLOR NAME[x]/Kleurnaam[x]",
              },
              {
                "name": "Order form: Retrieve from Table1, IF PMS PRESENT: USE PMS ELSE: COLOR NAME[x]/Kleurnaam[x]",
              }
            ],
          }
        },
        "barcode": {
          "ean_barcode": "Order form: EAN/UPC-code",
          "ean_barcode_type": "Default: EAN13, if empty ean_barcode: \"Geen barcode\""
        }
      }
    },
    "briefing": "Dit is een test briefing die vanuit de xml in de portal wordt ingelezen."
  }
}

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# client = openai.OpenAI(
#     # This is the default and can be omitted
#     api_key=OPENAI_API_KEY
# )

def process_gpt(df, email):
    try:
        messages = [
            {"role": "system",
             "content": "You are a helpful assistant designed to output JSON. You should also be capable of performing simple plus, minus, divide math operations"},
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": """Role: Account manager processing order forms. You are capable of performing simple plus, minus, divide math operations

                        I have an ERP order form in .json. I have added comments to the keys in the value of the JSON. These comments include information about how we need to fill in the value for the given key. The ERP form is given below here. Now I will first send you the .json then after that I will give you the information you need to fill in the form. Only then start responding.

                        It is possible that not all information is present to fill in all fields. When there is no information and no default value given, we can assume its missing and therefore leave the field empty.
                        """
                    },
                    {
                        "type": "text",
                        "text": "This is the ERP JSON FORM:"
                    },
                    {
                        "type": "text",
                        "text": str(comments_no_default)
                    }
                ]
            },
        ]

        content = [
            {
                "type": "text",
                "text": "You should return the filled in ERP json using the data given below. Please look carefully at the color and whether we need to use the color name or the PMS ID. We might have more colors than given in the example ERP json"
            },
            {
                "type": "text",
                "text": "Email text"
            },
            {
                "type": "text",
                "text": email
            }
        ]

        for index, row in df.iterrows():
            kvs = row['kvs']
            table_1 = row['table_1']
            content.append({
                "type": "text",
                "text": "Key-value pairs"
            })
            content.append({
                "type": "text",
                "text": str(kvs)
            })
            content.append({
                "type": "text",
                "text": "Table 1 color name or PMS ID"
            })
            content.append({
                "type": "text",
                "text": str(table_1)
            })

        user_role = {
            "role": "user",
            "content": content
        }

        messages.append(user_role)

        print(messages)

        return True

        # response = client.chat.completions.create(
        #     model="gpt-4o",
        #     response_format={"type": "json_object"},
        #     messages=messages
        # )
        # response_content = json.loads(response.choices[0].message.content)
        # return response_content
    except Exception as e:
        print(e)
        return {}
