from faker import Faker # libreria para nombres falsos
import csv
import pandas as pd
from datetime import datetime, time
import random
import os

# Generar los datos de clientes en el formulario de google (mas especifico, con mas datos)
def generar_datos_clientes(n_clientes: int):
	fake = Faker(['es_CL', 'es_AR', 'es_MX'])

	data = [["id", "rut", "nombre", "apellido", "genero", "fecha_nacimiento", 
	"correo", "telefono", "fecha_inscripcion", "membresia", "sector vivienda"]] # header del csv

	for _id in range(1, n_clientes + 1):
		rand = fake.random_int(min=1, max=2)

		prefijo = str(fake.random_int(min=9, max=21)).zfill(2) #prefijo para el rut en cierto rango
		resto_rut = fake.numerify(text=".###.###-")
		verificador = fake.random_element(elements=("1","2","3","4","5","6","7","8","9","0","k", ""))
		rut_correcto = f"{prefijo}{resto_rut}{verificador}"

		rut_final = fake.random_element(elements=(rut_correcto, 
		rut_correcto.replace(".", "").replace("-", ""), rut_correcto.replace(".",""))) # 21.606.429-1 , 21606429-1 , 216064291

		genero = fake.random_element(elements=("femenino", "masculino", "mujer", "hombre", "Femenino", "Masculino", "Mujer", "Hombre",))

		nombre = fake.first_name_female() if genero in ["femenino","mujer","Femenino","Mujer"] else fake.first_name_male()
		if len(nombre.split(" ")) > 1:
			nombre = nombre.split(" ")[0] # quedarse con solo el primer nombre
		nombre = fake.random_element(elements=(nombre, nombre.upper(), nombre.lower()))

		apellido = fake.last_name()
		if len(apellido.split(" ")) > 1:
			apellido = apellido.split(" ")[0]
		apellido = fake.random_element(elements=(apellido, apellido.upper(), apellido.lower()))


		nacimiento = fake.date_of_birth(minimum_age=22, maximum_age=65)
		fecha_nacimiento = nacimiento.strftime("%d-%m-%Y")


		correo = fake.random_element(elements=(f'{nombre}@gmail.com',f'{nombre}@gmailcom',f'{nombre}gmail.com',f'{nombre}{fake.random_int(min=1, max=10)}@gmail.com'))
		telefono = fake.random_element(elements=(fake.numerify(text="9########"), fake.numerify(text="+569########"), fake.numerify(text="+56 9########"), fake.numerify(text="+56 9 ########")))

		fecha_objeto = fake.date_between(start_date='-4y', end_date='-1y')
		fecha_inscripcion = fecha_objeto.strftime("%d-%m-%Y")
		
		membresia = fake.random_element(elements=('Basica','basica','basica', 'BASICA','basica','pro','Pro','PRO'))
		sector_vivienda = fake.random_element(elements=('temuco', 'pedro de valdivia','padre las casas', 'fundo el carmen', 'los conquistadores', 'barrio ingles'))

		data.append([_id, rut_final, nombre, apellido, genero, fecha_nacimiento, 
		correo, telefono, fecha_inscripcion, membresia, sector_vivienda])

	# Open file and write line by line
	with open("datasets/bronze_clientes.csv", "w", newline="", encoding="utf-8") as file:
		writer = csv.writer(file)
		for row in data:
			writer.writerow(row)  # Writes one line at a time

# Generar los datos de la tabla ventas
def generar_datos_ventas(n_ventas: int):
	fake = Faker(['es_CL', 'es_AR', 'es_MX'])
	ventas = [["id", "id_cliente", "id_vendedor", "tienda", "fecha", "metodo_pago", "factura", "descuento", "total"]]

	with open('datasets/bronze_detalle_ventas.csv', mode='w', newline='', encoding='utf-8') as f_detalle:
		writer_detalle = csv.writer(f_detalle)
		writer_detalle.writerow(['id_venta', 'id_producto', 'cantidad', 'precio_unitario'])

	for _id in range(1, n_ventas + 1):
		rand = fake.random_int(min=1, max=250)
		cliente_id = 0 if rand > 100 else rand
		id_vendedor = fake.random_int(min=1, max=9)
		tienda = fake.random_element(elements=('Hayden 102', 'Pedro Salinas 0295', 'Av Javierra Carrera 045')) # 3 Tiendas

		fecha = generar_fecha_hora_controlada()
		metodo_pago = fake.random_element(elements=('efectivo','efectivo','efectivo','debito','debito','debito','debito','debito','debito','transferencia','credito'))
		factura = fake.random_element(elements=('si','no','no','no','no'))

		descuento = obtener_descuento(cliente_id)
		total_inicial = generar_datos_detalle_venta(_id, fake)
		total = total_inicial * (1 - descuento/100)

		ventas.append([_id, cliente_id, id_vendedor, tienda, fecha, metodo_pago, factura,descuento, round(total)])
		
	with open("datasets/bronze_ventas.csv", "w", newline="", encoding="utf-8") as file:
		writer = csv.writer(file)
		for row in ventas:
			writer.writerow(row)	

# Generar datos de la tabla detalle_venta
def generar_datos_detalle_venta(id_venta: int, fake: Faker) -> int:
	cantidad_productos = fake.random_int(min=1, max=10)
	lista_detalle = []
	precio_total  = 0
	for _ in range(cantidad_productos):
		codigo, nombre, precio, cantidad = obtener_datos_producto(fake)
		precio = int(precio.strip().replace("$", "").replace(".", ""))
		precio_total += precio * int(cantidad)

		detalle = {
		'id_venta':id_venta,
        'id_producto': codigo,
        'cantidad': cantidad,
        'precio_unitario': precio
    		}
		lista_detalle.append(detalle)

	with open('datasets/bronze_detalle_ventas.csv', mode='a', newline='', encoding='utf-8') as archivo:
		nombres_columnas = ['id_venta', 'id_producto', 'cantidad', 'precio_unitario']
		escritor = csv.DictWriter(archivo, fieldnames=nombres_columnas, delimiter=';')
    
		escritor.writerows(lista_detalle)
	
	return precio_total

# Obtener los datos necesarios de un producto
def obtener_datos_producto(fake: Faker):
	df = pd.read_csv('datasets/no_borrar/bronze_productos.csv', sep=';') 
	producto_azar = df.sample(n=1).iloc[0]
	
	codigo = producto_azar['Código']
	nombre = producto_azar['Nombre del producto']
	precio = producto_azar['Precio + IVA']
	cantidad = fake.random_int(min=1, max=15)
	
	print(f"Código Azar: {codigo} | Producto: {nombre} | {precio} | Cantidad: {cantidad}")
	return codigo, nombre, precio, cantidad


####################
###### utils #######
####################

# Funcion para devolver el descuento a aplicar segun tipo de cliente. Si no es cliente
# Se aplica 0, si es basico 10% y si es pro 15%

def obtener_descuento(id_cliente: int):
	df_clientes = pd.read_csv("datasets/bronze_clientes.csv")
	membresias = dict(zip(df_clientes['id'], df_clientes['membresia'].str.lower()))

	membresia = membresias.get(id_cliente, "ninguna")

	if id_cliente > 0 and membresia in ('Basica','basica','BASICA'):
		descuento = 10

	if id_cliente > 0 and membresia in ('Pro','pro','PRO'):
		descuento = 15

	if id_cliente == 0:
		descuento = 0

	return descuento
	

# Funcion para generar un fecha y hora en formato correcto y aleatorio
def generar_fecha_hora_controlada():
    fecha_base = Faker('es_CL').date_between(
        start_date=datetime(2020, 1, 1), 
        end_date=datetime(2025, 12, 31)
    )
    
    hora = random.randint(9, 18)
    minuto = random.randint(0, 59)
    segundo = random.randint(0, 59)
    
    hora_base = time(hora, minuto, segundo)
    
    fecha_hora_final = datetime.combine(fecha_base, hora_base)
    
    return fecha_hora_final

# Funcion para agregar una nueva fila a los productos con el precio de venta, dejando asi el precio mas iva como el precio costo de compra
def agregar_precio_venta(ruta_origen, ruta_destino):
    df = pd.read_csv(ruta_origen, sep=';')
    
    precio_iva_limpio = (
        df['Precio + IVA']
        .astype(str)
        .str.replace('$', '', regex=False)
        .str.replace('.', '', regex=False)
        .str.strip()
    )

    precio_iva_num = pd.to_numeric(precio_iva_limpio)
 
    precio_venta_num = (((precio_iva_num * 2) + (precio_iva_num * 2 * 0.19))/10).round() * 10
    
    df['Precio venta'] = precio_venta_num.apply(lambda x: f" ${x:,.0f} ".replace(",", "."))
    
    df.to_csv(ruta_destino, sep=';', index=False, encoding='utf-8')
    print(f"Nuevo archivo generado con éxito en: {ruta_destino}")


def main():
	if os.path.isfile("datasets/bronze_clientes.csv"):
		os.remove("datasets/bronze_clientes.csv")  # Borrar clientes generados
		print("Archivo bronze_clientes.csv eliminado.")
	if os.path.isfile("datasets/bronze_ventas.csv"):
		os.remove("datasets/bronze_ventas.csv")  # Borrar ventas generadas
		print("Archivo bronze_ventas.csv eliminado.")
	if os.path.isfile("datasets/bronze_detalle_ventas.csv"):
		os.remove("datasets/bronze_detalle_ventas.csv")  # Borrar detalle de ventas generadas
		print("Archivo bronze_detalle_ventas.csv eliminado.")
	
	generar_datos_clientes(100)
	generar_datos_ventas(500)
	print("\n")
	print("=" * 40)
	print("Se han generado correctamente los datos.")
	print("=" * 40)
	return

if __name__ == "__main__":
	#ruta_original = "datasets/no_borrar/bronze_productos.csv"
	#ruta_nueva = "datasets/no_borrar/bronze_productos_nuevo.csv"
	#agregar_precio_venta(ruta_original, ruta_nueva)

	main()