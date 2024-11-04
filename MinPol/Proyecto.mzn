% Parámetros
int: n;  % número total de personas
int: m;  % número de opiniones posibles
array[1..m] of int: p;  % distribución inicial
array[1..m] of float: v;  % valores de las opiniones
array[1..m] of float: ce;  % costos extra
array[1..m,1..m] of float: c;  % matriz de costos
float: ct;  % costo total máximo
int: maxM;  % máximo de movimientos

% Variables
array[1..m,1..m] of var 0..n: x;  % movimientos de personas
array[1..m] of var bool: y;  % opiniones que reciben cuando estaban vacías
array[1..m] of var 0..n: p_final;  % distribución final

% Restricciones
constraint forall(j in 1..m)(
    p_final[j] = p[j] + sum(i in 1..m)(x[i,j]) - sum(k in 1..m)(x[j,k])
);

constraint forall(i in 1..m)(
    sum(j in 1..m)(x[i,j]) <= p[i]
);

constraint sum(i,j in 1..m)(
    c[i,j] * (1.0 + int2float(p[i])/int2float(n)) * int2float(x[i,j])
) + sum(j in 1..m)(
    ce[j] * bool2float(y[j]) * int2float(sum(i in 1..m)(x[i,j]))
) <= ct;

constraint sum(i,j in 1..m)(
    abs(j-i) * x[i,j]
) <= maxM;

constraint forall(j in 1..m)(
    y[j] = (p[j] = 0 /\ sum(i in 1..m)(x[i,j]) > 0)
);

constraint sum(i in 1..m)(p_final[i]) = n;

% Función auxiliar para calcular la mediana ponderada
function var float: weighted_median(array[int] of var int: dist, array[int] of float: vals) =
    let {
        int: total = sum(dist);
        var float: mid = int2float(total) / 2.0;
        array[1..m] of var float: cum = [ sum(j in 1..i)(int2float(dist[j])) | i in 1..m ];
    } in
    sum(i in 1..m)(
        vals[i] * bool2float(cum[i-1] < mid /\ mid <= cum[i])
    );

% Función objetivo
solve minimize sum(i in 1..m)(
    int2float(p_final[i]) * abs(v[i] - weighted_median(p_final, v))
);

% Output
output [
    "Movimientos:\n",
    concat(i,j in 1..m where fix(x[i,j]) > 0)(
        "De opinión " ++ show(i) ++ " a " ++ show(j) ++ ": " ++ show(fix(x[i,j])) ++ "\n"
    ),
    "\nDistribución final:\n",
    concat(i in 1..m)(
        "Opinión " ++ show(i) ++ ": " ++ show(fix(p_final[i])) ++ "\n"
    )
];
