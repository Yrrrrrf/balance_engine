# [Balance Engine](https://github.com/Yrrrrrf/balance_engine): Fase 1 - Ideación

## Información General
- **Nombre del Equipo:** [Firedge Innovators](https://app.genius-arena.com/participation_info/18/talent-hackathon-2025?team_id=14066&ppro_id=4870)
- **Nombre del Proyecto:** [Balance Engine](https://github.com/Yrrrrrf/balance_engine)
- **Track:** Production Planning: Linear Programming and automation through Python - Micron

## Integrantes
- [Fernando Bryan Reza Campos](https://www.linkedin.com/in/fernando-reza-campos/)
- Perla Edith Lugo Hernandez
- [Kevin Alexis Martinez Sanchez](https://www.linkedin.com/in/kevin-alexis-mart%C3%ADnez-s%C3%A1nchez-667963193/)
- Christian Daniel Ponce de León

## Problemática
En la industria manufacturera moderna, las empresas enfrentan un desafío crítico: equilibrar eficientemente la producción con la demanda mientras optimizan el uso de recursos limitados.

Las soluciones actuales resultan inadecuadas:
- Hojas de cálculo manuales propensas a errores
- Software genérico sin optimización matemática
- Sistemas ERP costosos con difícil integración a procesos existentes

Según estudios recientes, las ineficiencias en planificación de producción generan:
- **Exceso de inventario:** 22-25% en empresas manufactureras
- **Desperdicio de materias primas:** 18-20% de recursos utilizados
- **Capacidad productiva subutilizada:** 12-15% en promedio

## Nuestra Solución

**Balance Engine** es una herramienta especializada que utiliza programación lineal para optimizar automáticamente los planes de producción, equilibrando oferta y demanda mientras minimiza costos operativos.

### Arquitectura Tecnológica

La solución se construye sobre una arquitectura híbrida:

1. **Motor de Optimización en Rust:**
    - Núcleo de alto rendimiento para resolver problemas complejos de programación lineal
    - Implementación eficiente de algoritmos Simplex e Interior-Point
    - Procesamiento de alto rendimiento para problemas de gran escala
2. **Interfaz Python:**  
    - API intuitiva para integración con sistemas existentes
    - Procesamiento de datos y validación de entradas
    - Generación de visualizaciones y reportes

Esta combinación ofrece rendimiento superior (10-50x más rápido que soluciones puramente Python) manteniendo la facilidad de integración con sistemas empresariales existentes.

### Capacidades Principales
- **Planificación Óptima:** Determina cantidades precisas a producir para satisfacer demanda con inventario mínimo
- **Gestión de Inventarios:** Calcula automáticamente niveles óptimos de stock de seguridad
- **Asignación de Recursos:** Distribuye eficientemente recursos limitados entre líneas de producción
- **Proyecciones Avanzadas:** Modela escenarios futuros para anticipar problemas

## Marco Teórico de Programación Lineal

El sistema utiliza modelos matemáticos avanzados específicamente adaptados para planificación de producción:

$$
\text{Minimizar: } Z = c_1x_1 + c_2x_2 + \cdots + c_nx_n
$$

Sujeto a:

$$
\begin{aligned}
  a_{11}x_1 + a_{12}x_2 + \cdots + a_{1n}x_n &\leq b_1 \\
  a_{21}x_1 + a_{22}x_2 + \cdots + a_{2n}x_n &\leq b_2 \\
  &\vdots \\
  x_i &\geq 0 \text{ para todo } i
\end{aligned}
$$

Donde:
- $ x_i $ representa cantidades a producir
- $ c_i $ representa costos unitarios
- $ a_{ij} $ representa uso de recursos
- $ b_i $ representa disponibilidad de recursos


Esta formulación permite:
- **Optimización Determinista:** Garantiza soluciones óptimas y reproducibles
- **Resolución Eficiente:** Implementa métodos avanzados para problemas de gran escala
- **Flexibilidad Configurable:** Incorpora restricciones personalizadas según necesidades específicas

## Criterios de Evaluación

### Alto Impacto
- **Reducción de Costos:** Potencial para disminuir exceso de inventario (22-25%) y desperdicio de materias primas (18-20%)
- **Optimización de Recursos:** Mejora en la utilización de capacidad productiva (12-15%)
- **Adopción Universal:** Diseño híbrido permite implementación en empresas de cualquier tamaño

### Innovación y Creatividad
- **Arquitectura Híbrida:** Combinación innovadora de Rust (rendimiento) y Python (accesibilidad)
- **Enfoque Especializado:** Diseñado específicamente para resolver problemas de planificación de producción
- **Experiencia de Usuario:** Interfaz que oculta la complejidad matemática

### Escalabilidad
- **Técnica:** Maneja desde problemas pequeños hasta optimizaciones con millones de variables
- **Empresarial:** Implementación modular funcional para PyMEs y multinacionales
- **Geográfica:** Sin dependencias regionales, aplicable globalmente
- **Funcional:** Arquitectura extensible para nuevas restricciones y variables

### Viabilidad
- **Tecnologías Probadas:** Rust, Python y algoritmos establecidos de programación lineal
- **Integración Sencilla:** Interfaz Python facilita conexión con sistemas existentes
- **Mantenimiento Eficiente:** Documentación clara y estructura modular

### Mérito Técnico
- **Optimización Algorítmica:** Implementación eficiente de métodos adaptados para producción
- **Rendimiento Superior:** Núcleo Rust proporciona velocidades 10-50x más rápidas que soluciones Python puras
- **Precisión Matemática:** Resultados exactos con validación integrada

## Estado Actual y Próximos Pasos
**Demo:**
- Arquitectura general definida
- Interfaz Python-Rust funcional
- Sistema de compilación configurado

**En desarrollo:**
1. Implementación del solucionador de programación lineal
	- [Rust](https://doc.rust-lang.org) (motor de optimización)
	- [scipy lingprog](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html) (considerado para implementación)
	- [PuLP](https://pypi.org/project/pulp/) (considerado para implementación)
2. Desarrollo de modelos para casos de uso prioritarios
3. Creación de visualizaciones para resultados
4. Implementación de validación avanzada de entradas

![Balance Engine Implementation Plan](https://raw.githubusercontent.com/Yrrrrrf/balance_engine/refs/heads/main/resources/img/balance-engine-plan.jpeg)