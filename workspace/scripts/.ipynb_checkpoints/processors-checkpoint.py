import math
import os
from typing import Any, Dict, List, Tuple
from timeloopfe.v4spec.arch import Leaf, Storage
from timeloopfe.processors import Processor
from timeloopfe.v4spec.problem import Problem


def num2list_of_prime_factors(x: int):
    factors = []
    while x > 1:
        for i in range(2, x + 1):
            if x % i == 0:
                factors.append(i)
                x //= i
                break
    return factors


def _greedy_allocate_recursive(
    prime2count: Dict[int, int], allocated: int, capacity: int
) -> List[int]:
    best_alloc, best_primes = allocated, []
    for p in prime2count:
        if prime2count[p] == 0:
            continue
        if p * allocated > capacity:
            continue
        prime2count[p] -= 1
        following_alloc = _greedy_allocate_recursive(
            prime2count, allocated * p, capacity
        )
        new_alloc = math.prod(following_alloc) * p * allocated
        if new_alloc > best_alloc:
            best_alloc = new_alloc
            best_primes = [p] + following_alloc
        prime2count[p] += 1
    return best_primes


def greedy_allocate(
    factors: Dict[str, int], capacity: int
) -> Tuple[Dict[str, int], Dict[str, int]]:
    primes = {k: num2list_of_prime_factors(v) for k, v in factors.items()}
    allprimes = []
    for v in primes.values():
        allprimes += v
    prime2count = {p: allprimes.count(p) for p in set(allprimes)}

    chosen_primes = _greedy_allocate_recursive(prime2count, 1, capacity)
    factors_left = {k: v for k, v in factors.items()}
    chosen_factors = {k: 1 for k in factors}
    for p in chosen_primes:
        for k, v in factors_left.items():
            if v % p == 0:
                factors_left[k] //= p
                chosen_factors[k] *= p
                break
    return chosen_factors, factors_left


def greedy_allocate_multi_level(
    factors: Dict[str, int], capacities: List[int]
) -> List[Dict[str, int]]:
    chosen_level2factors = []
    factors_left = {k: v for k, v in factors.items()}
    for capacity in capacities:
        chosen_factors, factors_left = greedy_allocate(factors_left, capacity)
        chosen_level2factors.append(chosen_factors)
    return chosen_level2factors


class GreedyMapperProcessor(Processor):
    def __init__(
        self,
        factors: List = (),
        only_leaves: List = (),
        not_leaves: List = (),
        no_other_factors=False,
        temporal_permutations: List = (),
    ):
        """!@brief Initialize the processor.
        !@param factors: A list of factors to allocate.
        !@param only_leaves: A list of leaves to allocate over.
        !@param not_leaves: A list of leaves to not allocate over.
        !@param no_other_factors: If True, for target levels, do not allow any
                                  factors other than the ones specified in
                                  factors to be mapped.
        !@param temporal_permutations: A list of factors to permute temporally.
        """
        super().__init__()
        self.factors = factors
        self.only_leaves = only_leaves
        self.not_leaves = not_leaves
        self.no_other_factors = no_other_factors
        self.temporal_permutations = temporal_permutations

    def process(self):
        # SPATIAL FACTORS
        leaves = self.spec.get_nodes_of_type(Leaf)
        leaves = [l for l in leaves if l.spatial.get_fanout() > 1][::-1]
        factors = {f: self.spec.problem.instance[f] for f in self.factors}
        allocate_over = []
        capacities = []

        # Figure out how what factors to allocate and where
        for l in leaves:
            c = l.constraints
            for f in (c.spatial.factors, c.temporal.factors):
                for x in f:
                    n, _, v = f.splitfactor(x)
                    if n in factors:
                        factors[n] = factors[n] // int(v) if int(v) != 0 else 1

            if self.only_leaves and l.name not in self.only_leaves:
                continue
            if l.name in self.not_leaves:
                continue
            if not any(
                x in c.spatial.factors.get_factor_names() for x in self.factors
            ):
                allocate_over.append(l)
                allocated = c.spatial.factors.get_minimum_product()
                capacities.append(l.spatial.get_fanout() // allocated)

        # Allocate factors & update constraints
        allocs = greedy_allocate_multi_level(factors, capacities)
        for i, l in enumerate(allocate_over):
            l: Leaf
            for k, v in allocs[i].items():
                l.constraints.spatial.factors.add_eq_factor_iff_not_exists(
                    k, v
                )
            if self.no_other_factors:
                for k in self.spec.problem.shape.dimensions:
                    l.constraints.spatial.factors.add_eq_factor_iff_not_exists(
                        k, 1
                    )

        # If utilization is already >50%, can't add any more factors. Constrain
        # the rest to 1.
        for l in leaves:
            lfactors = l.constraints.spatial.factors
            spatial_factor_min = lfactors.get_minimum_product()
            if spatial_factor_min > l.spatial.get_fanout() / 2:
                for k in self.spec.problem.shape.dimensions:
                    lfactors.add_eq_factor_iff_not_exists(k, 1)

        # TEMPORAL PERMUTATIONS
        leaves = self.spec.get_nodes_of_type(Storage)
        for l in leaves:
            if l.name in self.not_leaves:
                continue
            if self.only_leaves and l.name not in self.only_leaves:
                continue
            for f in self.temporal_permutations[::-1]:
                if f not in l.constraints.temporal.permutation:
                    l.constraints.temporal.permutation.append(f)


class VariableSetter(Processor):
    def __init__(self, set_dicts: List[Dict[str, Any]], set_files: List[str]):
        """!@brief Initialize the processor.
        !@param set_dicts: A list of dictionaries with which to set variables.
        !@param set_files: A list of files with which to set variables.
        """
        super().__init__()

        def listify(x):
            return x if isinstance(x, (list, tuple)) else [x]

        self.set_dicts = listify(set_dicts)
        self.set_files = listify(set_files)

    def process(self):
        to_set = {}
        for d in self.set_dicts:
            to_set.update(d)
        for f in self.set_files:
            for line in open(f).readlines():
                if line.strip().startswith("#"):
                    continue
                k, v = line.split("=")
                to_set[k.strip()] = v.strip()
        for k, v in to_set.items():
            self.spec.variables[k.strip()] = v.strip()
            self.logger.info("Set variable: %s = %s", k.strip(), v.strip())


class ArtifactProcessor(Processor):
    def init_elems(self):
        super().init_elems()
        with self.responsible_for_removing_elems():
            Problem.init_elem("layer_name", str)
            Problem.init_elem("model_name", str)
            Problem.init_elem("densities", dict)

    def __init__(
        self,
        isaac: bool,
        raella_bert: bool,
        vars_from: str = None,
        use_typical_statistics: bool = False,
    ):
        """!@brief Initialize the processor.
        !@param isaac: If True, apply ISAAC adjustments.
        !@param raella_bert: If True, apply Raella BERT adjustments.
        !@param vars_from: If not None, read variables from this file.
        !@param use_typical_statistics: If True, use typical values instead of
                                    recorded values.
        """
        super().__init__()
        self.isaac = isaac
        self.raella_bert = raella_bert
        self.vars_from = vars_from
        self.use_typical_statistics = use_typical_statistics

    def process(self):
        variables = self.spec.variables
        layer_name = self.spec.problem.pop("layer_name")
        densities = self.spec.problem.pop("densities")
        _ = self.spec.problem.pop("model_name")
        # Read variables from the variables file
        if self.vars_from:
            vars_from = self.vars_from
            if os.path.isdir(self.vars_from):
                vars_from = f"{self.vars_from}/{layer_name}"
            for l in open(vars_from, "r").readlines():
                k, v = l.split("=")
                variables[k.strip()] = v.strip()

        # Grab statistics from the layer YAML file
        # (We don't do this for RAELLA becaus RAELLA adapts to each layer
        # so RAELLA's stats are more complicated to get.)
        if self.isaac and not self.use_typical_statistics:
            self.logger.info("Applying ISAAC adjustments")
            input_dist = densities["Inputs"]["unsigned_offset"]
            weight_dist = densities["Weights"]["unsigned_offset_invert_dense"]
            # avg_input = 0
            avg_weight = 0
            for i, v in enumerate(input_dist):
                # avg_input += v
                avg_weight += weight_dist[i] * (2 if i % 2 == 0 else 1)
            # variables["AVERAGE_INPUT_VALUE"] = avg_input / len(input_dist)
            variables["AVERAGE_WEIGHT_VALUE"] = avg_weight / len(weight_dist)

        # # ISAAC uses 2b cells (0-3) while RAELLA uses 4b (0-15).
        # # For fairness, everyone uses the same ReRAM devices. ISAAC uses the
        # # least-significant 2b, saving power.
        w = str(variables["AVERAGE_WEIGHT_VALUE"])
        variables["AVERAGE_WEIGHT_VALUE"] = (
            w + " / 15 * " + str(max(2 ** variables["BITS_PER_CELL"] - 1, 1))
        )

        # For BERT, RAELLA processes positive/negative input activations
        # separately. Doubles the latency and the number of ADC activations.
        # Due to the way we recirded average input values, average input
        # value is also doubled.
        if self.raella_bert:
            doubles = [
                "ADC_ACTION_SHARE",
                "CROSSBAR_LATENCY",
                "AVERAGE_INPUT_VALUE",
            ]
            for t in doubles:
                variables[t] = f"{variables[t]} * 2"
        elif self.use_typical_statistics and "bert" in layer_name.lower():
            variables["AVERAGE_INPUT_VALUE"] = 0.5
