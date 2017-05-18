######################################################################
# Sistemas Operativos, Proyecto Final : Simulador de memoria virtual
# Luis Castillo
######################################################################

"""
El programa simula un manejador de memoria virtual utilizando paginacion 
con el metodo de reemplazo FCFC y al final mide su rendimiento.
Para el simulador de memoria virtual se manejaron dos clases, 
una es la memoria virtual para poder almacenar los procesos y la otra es
en si un proceso que tiene distintos atributos como su tiempo de llegada,
su tiempo de salida, su localizacion, etc.
"""
from math import ceil
from datetime import datetime

RAM_SIZE = 2048 # Tamano de la memoria principal
VM_SIZE = 4096 # Tamano de la memoria virtual
FRAME_SIZE = 8 # Tamano de los frames

class VirtualMemory:

	def __init__(self): # se define el objeto
		self.processTable = {}
		self.countSwapIn = 0
		self.countSwapOut = 0

	#metodos
	# se crea una tupla donde van a estar guardados todos los procesos
	# con su id y su tiempo de llegada
	def addProcess(self, ident, time, process):
		self.processTable[ident] = time, process

	def getTime(self, ident):
		return self.processTable[ident]

	def iteritems(self): # despliega informacion de cierto proceso
		for i in self.processTable:
			print 'id: {} timestamp: {}'.format(i, self.processTable[i][0])

	def getOlder(self): # obtiene el proceso mas viejo de la tabla de procesos
		for i in self.processTable:
			self.updateProcessLocation(self.processTable[i][1])
		older = None
		min = 1000000000000000000000
		for i in self.processTable:
			if self.processTable[i][0] < min and self.processTable[i][1].location == 'M':
				min = self.processTable[i][0]
				older = i
		return older, self.processTable[older][1]

	# metodo para realizar swap
	def swapPages_FIFO(self, process, newSize):
		olderId, older = vm.getOlder()
		olderSize = older.sizeFrames
		countFIFO = 0
		try:
			for page in older.pagelist:
				if page[2] == 'M':
					if countFIFO >= newSize:
						break
					else:
						vm.frameAssign(page[0], older, S)
						page[2] = 'S'
						M[page[1]] = 0
						countFIFO += 1
						self.countSwapOut += 1
		except IndexError:
			pass

		vm.updateProcessLocation(older)
		return older

	# metodo que busca los frames adecuados para asignacion
	def frameAssign(self,pageNumber,process,array):
		if array == M:
			ramSize = RAM_SIZE
			ad = 'M'
		else:
			ramSize = VM_SIZE
			ad = 'S'
		for i in range(0,ramSize,FRAME_SIZE):
			if array[i] == 0: #si la frontera es 0 esta desocupada
				array[i] = process.ident #ocupamos la pagina
				process.pagelist[pageNumber] = [pageNumber, i, ad] #guarda en la lista de memorias el marco
				if ad == 'S':
					print ('pagina {} del proceso {} swappeada a la posicion {}'
						  ' del area de swapping'.format(pageNumber, process.ident, i))
				return

	# metodo que recorre el arreglo para checar si hay los lugares suficientes
	def fits(self,size,array):
		count = 0
		for i in range(0,RAM_SIZE,FRAME_SIZE):
			if array[i] == 0:
				count = count + 1
		return size <= count

	# metodo para contar el numero de frames libres en M o S
	def numberFreeFrames(self, array):
		if array == M:
			ramSize = RAM_SIZE
		else:
			ramSize = VM_SIZE
		count = 0
		for i in range(0,ramSize,FRAME_SIZE):
			if array[i] == 0:
				count += 1
		return count

	# Actualiza el atributo de la locacion de cierto proceso
	def updateProcessLocation(self,process):
		flag = True
		for i in process.pagelist:
			if i[2] == 'M' or i[2] == None:
				flag = False
		if flag:	
			process.location = 'S'

class Process:
	# se define el objeto proceso
	def __init__(self,size,ident):
		self.ident = ident
		self.size = float(size)
		self.sizeFrames = int(ceil(self.size/FRAME_SIZE))
		self.location = None # M -> memoria real y S -> memoria virtual
		self.startTime = 0
		self.lifeTime = 0
		self.pageFaults = 0
		self.pagelist = [[i, 0, None] for i in range(self.sizeFrames)]
		if vm.numberFreeFrames(S) < self.sizeFrames:
			print 'Area de Swapping agotada. Id: {}'.format(self.ident)
			# con el return finaliza cualquier metodo, en este caso el constructor
			return
		t = datetime.now()
		now = 60*1000000*((t.day*24 + t.hour)*60 + t.minute) + t.microsecond
		self.startTime = now
		vm.addProcess(ident, now, self)
		self.location = 'M'
		countAF = 0 # count assigned frames
		for page in self.pagelist:
			# checar frames libres
			if vm.numberFreeFrames(M) > 0:
				vm.frameAssign(page[0], self, M)
				countAF += 1
			else:
				#mientras no cabe llama a la funcion de fifo para hacer espacio
				# se agrega a la tabla de procesos si no agota area de swap
				if countAF <= self.sizeFrames:
					vm.swapPages_FIFO(self, self.sizeFrames - countAF)
				vm.frameAssign(page[0], self, M)
				countAF += 1
				vm.updateProcessLocation(self)

#loadProcess
def loadProcess(args):
	"""
	funcion para cargar el proceso, primero verifica que no exceda el Tamano
	maximo de M y posteriormente lo asigna, si ya no hay espacio ocurre swap
	"""
	size = args[0]
	id = args[1]
	print '\n'
	print 'P {} {}'.format(int(args[0]),int(args[1]))
	if float(size) > RAM_SIZE:
		print 'Proceso {} mayor a la MEM_RAM.'.format(id)
		return
	p = Process(size, id)
	try:
		tmp = [ i[1]/FRAME_SIZE for i in vm.processTable[id][1].pagelist]
		print 'Se asignaron los marcos de pagina {} al proceso {}'.format(tmp,id)
	except KeyError:
		pass

#freeUpMem
def freeUpMem(args):
	"""
	Libera de la memoria el proceso seleccionado
	"""
	id = args[0]
	print '\n'
	print 'L {}'.format(id)
	try:
		process = vm.processTable[id][1]
	except KeyError:
		print 'El proceso {} no existe'.format(id)
		return
	for i in process.pagelist:
		if i[2] == 'M':
			# poner 0 en M
			M[i[1]] = 0
			print ('Se libera marco {} de memoria real'
				   ' que ocupaba el proceso {}'.format(i[1], id))
		else:
			S[i[1]] = 0
			print ('Se libera la posicion {} del area de swapping'
				  ' que ocupaba el proceso {}'.format(i[1], id))
		i[2] = None
	process.location = None
	t = datetime.now()
	now = 60*1000000*((t.day*24 + t.hour)*60 + t.minute) + t.microsecond
	process.lifeTime = now - process.startTime

#accessVD
def accessVD(args):
	"""
	funcion para accesar cierta direccion virtual, es decir localizar 
	donde se encuentra la pagina que contiene esa direccion. Primero se busca
	el proceso y si esta en M simplemente se despliega la direccion, en caso
	contrario se realiza swap y se trae a M la direccion adecuada
	"""
	d = int(args[0])
	id = args[1]
	m = int(args[2])
	print '\n'
	print 'A {} {} {}'.format(d, id, m)
	try:
		process = vm.processTable[id][1]
	except KeyError:
		print 'El proceso {} no existe'.format(id)
		return
	frame = d / FRAME_SIZE
	try:
		frameLoc = process.pagelist[frame]
	except IndexError:
		print 'Direccion invalida'
		return

	if frameLoc[2] == 'M':
		print 'Direccion real {}'.format(frameLoc[1] + d % FRAME_SIZE)
		
	elif vm.numberFreeFrames(M) > 0:
		ps = frameLoc[1] # guardar la posicion que tenia en S
		vm.frameAssign(frameLoc[0], process, M)
		vm.updateProcessLocation(process)
		frameLoc = process.pagelist[frame]
		print 'Direccion real {}'.format(frameLoc[1] + d % FRAME_SIZE)
		print ('Se localizo la pagina {} del proceso {} '
			   'que estaba en la posicion {} de swapping'
			   ' y se cargo al marco {}'.format(
			   	frameLoc[0],id,ps,frameLoc[1]))
		vm.countSwapIn += 1
	else:
		process.pageFaults += 1
		ps = frameLoc[1] # guardar la posicion que tenia en S
		old = vm.swapPages_FIFO(process, 1)
		vm.frameAssign(frameLoc[0], process, M)
		vm.updateProcessLocation(process)
		frameLoc = process.pagelist[frame]
		print 'Direccion real {}'.format(frameLoc[1] + d % FRAME_SIZE)
		print ('Se localizo la pagina {} del proceso {} '
			   'que estaba en la posicion {} de swapping'
			   ' y se cargo al marco {}'.format(
			   	frameLoc[0],id,ps,frameLoc[1]))
		vm.countSwapOut += 1
		vm.countSwapIn += 1

#Statistics
def Statistics():
	"""
	Despliega las estadisticas y luego vuelve a inicializar todo
	"""
	print '\n'
	print "F"
	count = 0
	suma = 0
	for i in vm.processTable:
		p = vm.processTable[i][1]
		if p.location is not None:
			# print 'p location {}'.format(p.location)
			print '*Error* - se quedo cargado el proceso {}'.format(p.ident)
		if p.location is None:
			count += 1
			suma += p.lifeTime
			print 'turnaround time de proceso {} -> {}'.format(p.ident,p.lifeTime)
			print 'Numero de pageFaults de proceso {} -> {}'.format(
				p.ident,p.pageFaults)
	try:
		print 'turnaround promedio de los procesos terminados -> {}'.format(
				float(suma)/count)
		print 'Numero total de operaciones swapIn -> {}'.format(vm.countSwapIn)
		print 'Numero total de operaciones swapOut -> {}'.format(vm.countSwapOut)
	except ZeroDivisionError:
		print 'Error, no habia nada en memoria'
	
	# inicializar memoria virtual
	for i in range(RAM_SIZE):
		M[i] = 0
	for i in range(VM_SIZE):
		S[i] = 0
	vm.__init__()
	print '\n'
	print '*********Se reinicializa todo************'

# Se inicializan los arreglos M y S y se crea el objeto virtualMemory
M = [0 for i in range(RAM_SIZE)]
S = [0 for i in range(VM_SIZE)]
vm = VirtualMemory()

def main():
	filename = raw_input("Introduce el archivo de prueba: ")
	#filename = 'datos.txt'
	try:
		with open(filename, 'r') as f:
			lines = f.readlines()		
	except IOError:
		print 'Archivo invalido'
		return

	for line in lines:
		if line == '\n': # linea vacia, continua hasta encontrar comando
			continue
		if line.startswith(';'): # linea comentada para cuestiones de prueba
			continue
		codes = line.split()
		# validaciones
		if codes[0].upper() == 'P' and len(codes) == 3:
			try:
				type(int(codes[1]))
			except ValueError:
				print '\n'
				print 'Sintaxis incorrecta'
				continue
			try:
				type(int(codes[2]))
			except ValueError:
				print '\n'
				print 'Sintaxis incorrecta'
				continue
			loadProcess(codes[1:])
		elif codes[0].upper() == 'A' and len(codes) == 4:
			try:
				type(int(codes[1])) == int
			except ValueError:
				print '\n'
				print 'Sintaxis incorrecta'
				continue
			try:
				type(int(codes[2])) == int
			except ValueError:
				print '\n'
				print 'Sintaxis incorrecta'
				continue
			try:
				type(int(codes[3])) == int
			except ValueError:
				print '\n'
				print 'Sintaxis incorrecta'
				continue
			accessVD(codes[1:])
		elif codes[0].upper() == 'L' and len(codes) == 2:
			try:
				type(int(codes[1])) == int
			except ValueError:
				print '\n'
				print 'Sintaxis incorrecta'
				continue
			freeUpMem(codes[1:])
		elif codes[0].upper() == 'F':
			Statistics()
		elif codes[0].upper() == 'E':
			print 'babay'
			exit()
		else:
			print '\n'
			print 'Error en comando'

if __name__ == "__main__":                       
    main()