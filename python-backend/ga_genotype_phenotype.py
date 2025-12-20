"""
Genotype-Phenotype Mapping Module
==================================
Handles conversion between genotypes (GA representation) and phenotypes (actual solutions).
Includes grammar-based derivation trees for structured solutions.

Features:
- Flexible genotype representation (real-valued, binary, integer)
- Grammar-based expression generation
- Derivation tree building and validation
- Error handling for invalid phenotypes
"""

import numpy as np
import logging
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum
import re

logger = logging.getLogger(__name__)


class GenotypeType(Enum):
    """Supported genotype representations"""
    REAL_VALUED = "real"      # Continuous values in [0, 1]
    BINARY = "binary"         # Binary bits {0, 1}
    INTEGER = "integer"       # Integer values
    PERMUTATION = "permutation"  # Permutation (order matters)
    TREE = "tree"            # Tree structure


@dataclass
class GrammarRule:
    """Grammar rule for derivation trees"""
    symbol: str              # Non-terminal symbol (e.g., '<expr>')
    productions: List[List[Union[str, 'GrammarRule']]]  # List of production options
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate grammar rule"""
        errors = []
        if not self.symbol:
            errors.append("Symbol cannot be empty")
        if not self.productions:
            errors.append(f"Rule for {self.symbol} must have at least one production")
        return len(errors) == 0, errors


class GenotypeMapper(ABC):
    """Abstract base class for genotype-phenotype mapping"""
    
    def __init__(self, genotype_type: GenotypeType):
        self.genotype_type = genotype_type
    
    @abstractmethod
    def genotype_to_phenotype(self, genotype: np.ndarray) -> Any:
        """Convert genotype to phenotype (actual solution)"""
        pass
    
    @abstractmethod
    def phenotype_to_genotype(self, phenotype: Any) -> np.ndarray:
        """Convert phenotype back to genotype"""
        pass
    
    @abstractmethod
    def create_random_genotype(self, length: int) -> np.ndarray:
        """Create random valid genotype"""
        pass
    
    @abstractmethod
    def validate_phenotype(self, phenotype: Any) -> Tuple[bool, Optional[str]]:
        """Check if phenotype is valid"""
        pass


class RealValuedMapper(GenotypeMapper):
    """Maps real-valued genotypes [0,1] to constrained phenotypes"""
    
    def __init__(self, min_val: float = 0.0, max_val: float = 1.0):
        super().__init__(GenotypeType.REAL_VALUED)
        self.min_val = min_val
        self.max_val = max_val
    
    def genotype_to_phenotype(self, genotype: np.ndarray) -> np.ndarray:
        """Scale [0,1] genotype to [min_val, max_val] phenotype"""
        if not np.all(np.logical_and(genotype >= 0, genotype <= 1)):
            logger.warning("Genotype not in [0,1], clipping to valid range")
            genotype = np.clip(genotype, 0, 1)
        
        phenotype = self.min_val + genotype * (self.max_val - self.min_val)
        return phenotype
    
    def phenotype_to_genotype(self, phenotype: np.ndarray) -> np.ndarray:
        """Scale [min_val, max_val] phenotype back to [0,1] genotype"""
        phenotype = np.clip(phenotype, self.min_val, self.max_val)
        genotype = (phenotype - self.min_val) / (self.max_val - self.min_val + 1e-10)
        return genotype
    
    def create_random_genotype(self, length: int) -> np.ndarray:
        """Create random genotype in [0,1]"""
        return np.random.uniform(0, 1, length)
    
    def validate_phenotype(self, phenotype: Any) -> Tuple[bool, Optional[str]]:
        """Check if phenotype is numeric and in valid range"""
        try:
            phenotype_array = np.array(phenotype)
            if not np.issubdtype(phenotype_array.dtype, np.number):
                return False, "Phenotype must be numeric"
            if np.any(np.isnan(phenotype_array)) or np.any(np.isinf(phenotype_array)):
                return False, "Phenotype contains NaN or Inf values"
            if np.any(phenotype_array < self.min_val) or np.any(phenotype_array > self.max_val):
                return False, f"Phenotype values outside range [{self.min_val}, {self.max_val}]"
            return True, None
        except Exception as e:
            return False, f"Error validating phenotype: {str(e)}"


class BinaryMapper(GenotypeMapper):
    """Maps binary genotypes to various phenotypes"""
    
    def __init__(self, interpretation: str = "decimal"):
        """
        Args:
            interpretation: How to interpret binary string
                'decimal': Binary to decimal number
                'gray': Gray code to decimal
                'bits': Treat as individual bits
        """
        super().__init__(GenotypeType.BINARY)
        self.interpretation = interpretation
    
    def genotype_to_phenotype(self, genotype: np.ndarray) -> Union[int, np.ndarray]:
        """Convert binary genotype to phenotype"""
        if not np.all(np.logical_or(genotype == 0, genotype == 1)):
            logger.warning("Non-binary values found, rounding to 0 or 1")
            genotype = np.round(np.clip(genotype, 0, 1))
        
        if self.interpretation == "decimal":
            # Interpret as binary number
            binary_str = ''.join(genotype.astype(int).astype(str))
            phenotype = int(binary_str, 2) if binary_str else 0
        elif self.interpretation == "gray":
            # Gray code to binary
            genotype_int = genotype.astype(int)
            binary = genotype_int.copy()
            for i in range(1, len(binary)):
                binary[i] = binary[i] ^ binary[i-1]
            binary_str = ''.join(binary.astype(str))
            phenotype = int(binary_str, 2) if binary_str else 0
        else:  # "bits"
            phenotype = genotype
        
        return phenotype
    
    def phenotype_to_genotype(self, phenotype: Any) -> np.ndarray:
        """Convert phenotype back to binary genotype"""
        if self.interpretation == "bits":
            return np.array(phenotype, dtype=int)
        
        # Convert number to binary
        if isinstance(phenotype, (int, np.integer)):
            if phenotype < 0:
                logger.warning(f"Negative value {phenotype}, using absolute value")
                phenotype = abs(phenotype)
            binary_str = bin(phenotype)[2:]
        else:
            binary_str = str(phenotype)
        
        return np.array([int(b) for b in binary_str], dtype=float)
    
    def create_random_genotype(self, length: int) -> np.ndarray:
        """Create random binary genotype"""
        return np.random.randint(0, 2, length).astype(float)
    
    def validate_phenotype(self, phenotype: Any) -> Tuple[bool, Optional[str]]:
        """Check if phenotype is valid"""
        if self.interpretation == "bits":
            try:
                arr = np.array(phenotype)
                if not np.all(np.logical_or(arr == 0, arr == 1)):
                    return False, "Phenotype must contain only 0s and 1s"
                return True, None
            except:
                return False, "Cannot convert phenotype to array"
        else:
            if not isinstance(phenotype, (int, np.integer)):
                return False, "Phenotype must be integer"
            if phenotype < 0:
                return False, "Phenotype must be non-negative"
            return True, None


class GrammarMapper(GenotypeMapper):
    """Maps genotypes to phenotypes using context-free grammars"""
    
    def __init__(self, grammar: Dict[str, List[List[str]]], max_depth: int = 10):
        """
        Args:
            grammar: Grammar rules dict
                Key: non-terminal (e.g., '<expr>')
                Value: List of production rules (each rule is list of symbols)
            max_depth: Maximum derivation tree depth to prevent infinite recursion
        """
        super().__init__(GenotypeType.TREE)
        self.grammar = grammar
        self.max_depth = max_depth
        self._validate_grammar()
    
    def _validate_grammar(self):
        """Validate grammar structure"""
        if not self.grammar:
            raise ValueError("Grammar cannot be empty")
        
        logger.info(f"Validating grammar with {len(self.grammar)} rules")
        for symbol, productions in self.grammar.items():
            if not symbol.startswith('<') or not symbol.endswith('>'):
                logger.warning(f"Symbol '{symbol}' doesn't follow <name> format")
            if not productions:
                raise ValueError(f"Symbol '{symbol}' has no productions")
    
    def genotype_to_phenotype(self, genotype: np.ndarray) -> str:
        """
        Convert genotype to phenotype using grammar derivation.
        
        Uses genotype values to select productions from grammar.
        """
        if not np.all(np.logical_and(genotype >= 0, genotype <= 1)):
            logger.warning("Genotype not in [0,1], clipping")
            genotype = np.clip(genotype, 0, 1)
        
        try:
            # Start with start symbol (first rule)
            start_symbol = list(self.grammar.keys())[0]
            phenotype = self._derive(start_symbol, genotype, depth=0, gene_index=[0])
            
            is_valid, error = self.validate_phenotype(phenotype)
            if not is_valid:
                logger.warning(f"Generated invalid phenotype: {error}")
                phenotype = f"<error: {error}>"
            
            return phenotype
        except Exception as e:
            logger.error(f"Error in grammar derivation: {str(e)}")
            return f"<error: {str(e)}>"
    
    def _derive(self, symbol: str, genotype: np.ndarray, depth: int, 
                gene_index: List[int]) -> str:
        """Recursively derive string from symbol"""
        if depth > self.max_depth:
            logger.warning(f"Max derivation depth {self.max_depth} reached")
            return f"<depth_limit>"
        
        if not symbol.startswith('<'):
            # Terminal symbol
            return symbol
        
        if symbol not in self.grammar:
            logger.warning(f"Unknown symbol: {symbol}")
            return symbol
        
        # Select production using genotype
        productions = self.grammar[symbol]
        if gene_index[0] >= len(genotype):
            # Wrap around or use modulo
            gene_value = genotype[gene_index[0] % len(genotype)]
        else:
            gene_value = genotype[gene_index[0]]
        
        gene_index[0] += 1
        production_idx = int(gene_value * len(productions)) % len(productions)
        production = productions[production_idx]
        
        # Derive all symbols in production
        result = ""
        for sym in production:
            result += self._derive(sym, genotype, depth + 1, gene_index)
        
        return result
    
    def phenotype_to_genotype(self, phenotype: str) -> np.ndarray:
        """Convert phenotype back to genotype (approximation)"""
        # This is approximate - we create a random genotype that might produce similar phenotypes
        logger.warning("phenotype_to_genotype is approximate for grammar mapper")
        return np.random.uniform(0, 1, 10)
    
    def create_random_genotype(self, length: int) -> np.ndarray:
        """Create random genotype for grammar"""
        return np.random.uniform(0, 1, length)
    
    def validate_phenotype(self, phenotype: str) -> Tuple[bool, Optional[str]]:
        """Check if phenotype is valid string"""
        if not isinstance(phenotype, str):
            return False, "Phenotype must be a string"
        if phenotype.startswith("<error"):
            return False, "Phenotype contains error marker"
        if len(phenotype) > 10000:
            return False, "Phenotype string too long"
        return True, None


class DerivationTree:
    """
    Represents a grammar derivation tree.
    
    Useful for analyzing how phenotypes were derived and for
    tree-based crossover operations.
    """
    
    def __init__(self, symbol: str, production_idx: int = 0):
        self.symbol = symbol
        self.production_idx = production_idx
        self.children: List['DerivationTree'] = []
        self.depth = 0
    
    def add_child(self, child: 'DerivationTree'):
        """Add child node"""
        self.children.append(child)
        self.depth = max(self.depth, child.depth + 1)
    
    def to_string(self) -> str:
        """Convert tree back to string"""
        if not self.children:
            # Terminal
            return self.symbol
        
        result = ""
        for child in self.children:
            result += child.to_string()
        return result
    
    def get_all_nodes(self) -> List['DerivationTree']:
        """Get all nodes in tree (pre-order traversal)"""
        nodes = [self]
        for child in self.children:
            nodes.extend(child.get_all_nodes())
        return nodes
    
    def __repr__(self) -> str:
        return f"DerivationTree({self.symbol}, depth={self.depth}, children={len(self.children)})"


def test_genotype_phenotype_mapping():
    """Test genotype-phenotype mapping in command prompt"""
    print("\n" + "="*70)
    print("GENOTYPE-PHENOTYPE MAPPING TEST SUITE")
    print("="*70)
    
    # Test RealValuedMapper
    print("\n" + "-"*70)
    print("REAL-VALUED MAPPER")
    print("-"*70)
    
    mapper = RealValuedMapper(min_val=-10.0, max_val=10.0)
    genotype = np.array([0.0, 0.5, 1.0])
    phenotype = mapper.genotype_to_phenotype(genotype)
    print(f"\nGenotype: {genotype}")
    print(f"Phenotype (mapped to [-10, 10]): {phenotype}")
    
    genotype_back = mapper.phenotype_to_genotype(phenotype)
    print(f"Genotype (mapped back): {genotype_back}")
    
    is_valid, error = mapper.validate_phenotype(phenotype)
    print(f"Phenotype valid: {is_valid} {error if error else ''}")
    
    random_genotype = mapper.create_random_genotype(5)
    print(f"Random genotype: {random_genotype}")
    
    # Test BinaryMapper
    print("\n" + "-"*70)
    print("BINARY MAPPER - DECIMAL INTERPRETATION")
    print("-"*70)
    
    binary_mapper = BinaryMapper(interpretation="decimal")
    genotype = np.array([1, 0, 1, 0])
    phenotype = binary_mapper.genotype_to_phenotype(genotype)
    print(f"\nGenotype (binary): {genotype}")
    print(f"Phenotype (decimal): {phenotype}")
    
    genotype_back = binary_mapper.phenotype_to_genotype(phenotype)
    print(f"Genotype (mapped back): {genotype_back}")
    
    is_valid, error = binary_mapper.validate_phenotype(phenotype)
    print(f"Phenotype valid: {is_valid}")
    
    # Test BinaryMapper - bits
    print("\n" + "-"*70)
    print("BINARY MAPPER - BITS INTERPRETATION")
    print("-"*70)
    
    bits_mapper = BinaryMapper(interpretation="bits")
    genotype = np.array([1, 0, 1, 0, 1])
    phenotype = bits_mapper.genotype_to_phenotype(genotype)
    print(f"\nGenotype: {genotype}")
    print(f"Phenotype (bits): {phenotype}")
    
    is_valid, error = bits_mapper.validate_phenotype(phenotype)
    print(f"Phenotype valid: {is_valid}")
    
    # Test GrammarMapper
    print("\n" + "-"*70)
    print("GRAMMAR MAPPER - ARITHMETIC EXPRESSION")
    print("-"*70)
    
    grammar = {
        '<expr>': [
            ['<term>'],
            ['<term>', '+', '<term>'],
            ['<term>', '-', '<term>']
        ],
        '<term>': [
            ['<number>'],
            ['<number>', '*', '<number>'],
            ['<number>', '/', '<number>']
        ],
        '<number>': [
            ['1'],
            ['2'],
            ['3'],
            ['x']
        ]
    }
    
    grammar_mapper = GrammarMapper(grammar, max_depth=5)
    genotype = np.array([0.1, 0.5, 0.9, 0.2, 0.7, 0.3, 0.8])
    phenotype = grammar_mapper.genotype_to_phenotype(genotype)
    print(f"\nGenotype: {genotype}")
    print(f"Phenotype (derived): {phenotype}")
    
    is_valid, error = grammar_mapper.validate_phenotype(phenotype)
    print(f"Phenotype valid: {is_valid} {error if error else ''}")
    
    print("\n" + "-"*70)
    print("GRAMMAR MAPPER - LOGICAL EXPRESSION")
    print("-"*70)
    
    logic_grammar = {
        '<expr>': [
            ['<var>'],
            ['<var>', 'AND', '<var>'],
            ['<var>', 'OR', '<var>'],
            ['NOT', '<var>']
        ],
        '<var>': [
            ['x'],
            ['y'],
            ['z']
        ]
    }
    
    logic_mapper = GrammarMapper(logic_grammar, max_depth=4)
    genotypes_test = [
        np.array([0.1, 0.3, 0.5]),
        np.array([0.6, 0.8, 0.9]),
        np.array([0.2, 0.4, 0.7])
    ]
    
    print(f"\nLogic expressions generated:")
    for i, g in enumerate(genotypes_test):
        pheno = logic_mapper.genotype_to_phenotype(g)
        print(f"  {i+1}. Genotype {g} → {pheno}")
    
    # Test DerivationTree
    print("\n" + "-"*70)
    print("DERIVATION TREE")
    print("-"*70)
    
    tree = DerivationTree('<expr>')
    term_child = DerivationTree('<term>')
    number_child = DerivationTree('5')
    term_child.add_child(number_child)
    tree.add_child(term_child)
    
    print(f"\nTree: {tree}")
    print(f"Tree string: {tree.to_string()}")
    print(f"All nodes: {len(tree.get_all_nodes())} nodes")
    
    print("\n" + "="*70)
    print("✓ GENOTYPE-PHENOTYPE MAPPING TEST COMPLETED")
    print("="*70 + "\n")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(message)s'
    )
    test_genotype_phenotype_mapping()
