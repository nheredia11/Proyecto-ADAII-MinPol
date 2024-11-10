% Parámetros de entrada
int: n;  % Número total de personas
int: m;  % Número de opiniones posibles
array[1..m] of int: p;  % Número de personas que tienen cada opinión inicial
array[1..m] of float: v;  % Valor real de cada opinión
array[1..m, 1..m] of float: c;  % Costo de mover personas entre opiniones
array[1..m] of float: ce;  % Costo extra de mover a una opinión sin personas
float: ct;  % Costo total máximo permitido
int: maxM;  % Número máximo de movimientos permitidos

% Verificaciones de consistencia de datos
constraint assert(n > 0, "El número total de personas debe ser positivo");
constraint assert(m > 0, "El número de opiniones debe ser positivo");
constraint assert(sum(p) = n, "La suma de personas en cada opinión debe ser igual al total");

% Variables de decisión: número de personas que se mueven de opinión i a j
array[1..m, 1..m] of var 0..n: x;

% Función para obtener todos los valores de opiniones considerando la frecuencia
function array[int] of float: get_all_values(array[1..m] of float: values, array[1..m] of int: freqs) =
    let {
        array[1..sum(freqs)] of float: result = [ 
            values[i] | i in 1..m, j in 1..freqs[i]
        ]
    } in result;

% Obtener todos los valores para el cálculo de la mediana
array[1..n] of float: all_values = get_all_values(v, p);

% Cálculo de la mediana de las opiniones iniciales
float: median_value = if n mod 2 = 0 then
    (all_values[n div 2] + all_values[(n div 2) + 1]) / 2.0
else
    all_values[(n + 1) div 2]
endif;

% Calcular la nueva distribución de opiniones después de los movimientos
array[1..m] of var 0..n: new_p;
constraint forall(j in 1..m) (
    new_p[j] = p[j] + sum(i in 1..m where i != j)(x[i,j]) - sum(i in 1..m where i != j)(x[j,i])
);

% Restricciones de no movimiento a la misma opinión
constraint forall(i in 1..m) (x[i,i] = 0);

% Función objetivo: minimizar la polarización
var float: polarization = sum(i in 1..m) (new_p[i] * abs(v[i] - median_value));
solve minimize polarization;

% Restricciones

% Restricción de conservación de personas por opinión
constraint forall(i in 1..m) (
    sum(j in 1..m where i != j)(x[i,j]) <= p[i]
);

% Restricción de no negatividad en la nueva distribución
constraint forall(j in 1..m) (new_p[j] >= 0);

% Restricción de conservación del total de personas
constraint sum(new_p) = n;

% Restricción de costo total
var float: total_cost = sum(i,j in 1..m where i != j) (
    c[i,j] * x[i,j] * (1.0 + p[i] / n) + 
    if p[j] = 0 then ce[j] * x[i,j] else 0.0 endif
);
constraint total_cost <= ct;

% Restricción de número máximo de movimientos
var int: total_movements = sum(i,j in 1..m where i != j)(abs(i - j) * x[i,j]);
constraint total_movements <= maxM;

% Salida formateada
output [
    "Matriz de movimientos x[i,j]:\n",
    concat([
        if j = 1 then "\n" else "" endif ++
        show_float(0, 2, x[i,j]) ++ "\t"
        | i,j in 1..m
    ]),
    "\n\nNueva distribución de personas:\n",
    show(new_p),
    "\n\nPolarización final: ", show_float(2, 3, polarization),
    "\n\nCosto total: ", show_float(2, 3, total_cost),
    "\n\nMovimientos totales: ", show(total_movements)
];