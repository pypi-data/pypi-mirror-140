import EDA

def check_resize_image():
        list_result = EDA.resize_image('/Users/federicoruizruiz/Documents/GitHub/dani/DSFT1121/src/data/test_resources_jorge/images_to_predict',
                            28,
                            28,
                            False,
                            ['Prim','Sec','Terc','Cua'],
                            True)

        return list_result

def check_standarize_numbers(lista, tipo):
    list_result = EDA.standarize_numbers(lista, tipo)        
    return list_result


#list1 = check_resize_image()

list2 = check_standarize_numbers(['5,1','7','1','1'], 'integer') #ko fallo al convertir 5,1 a decimal
list3 = check_standarize_numbers(['5.1','7','1','1'], 'integer') #ko convierte 5.1 en 51 
list4 = check_standarize_numbers(['5,1','7','1','1'], 'double')  #ok
list5 = check_standarize_numbers(['5.1','7','1','1'], 'double') #ko convierte 5.1 en 51.0
list6 = check_standarize_numbers(['5,1','7','1','1'], 'decimal') #ok 
list7 = check_standarize_numbers(['5.1','7','1','1'], 'decimal') #ok 
