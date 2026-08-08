from typing import Dict, Any, List, Set

PRIMITIVE_SERIES = {'open','high','low','close','volume'}
# Non-basic/transform wrappers to ignore
TRANSFORMS = {
    'tf','count','countstreak','cum','cumulative','mom',
    'n_days_ago','n_weeks_ago','n_months_ago','n_years_ago',
    'round','ceil','floor','min','max','square','abs','crossover'
}


def _extract_ints_from_params(params: List[Any]) -> List[int]:
    out: List[int] = []
    for p in params:
        if isinstance(p, (int, float)):
            try:
                iv = int(p)
                out.append(iv)
            except Exception:
                pass
        elif isinstance(p, dict) and p.get('type') == 'number':
            try:
                iv = int(p.get('value'))
                out.append(iv)
            except Exception:
                pass
    return out


def extract_basic_indicator_specs(ast_node: Dict[str, Any], registry_functions: Set[str]) -> List[str]:
    """
    Extract basic indicator specifications dynamically from AST:
    - Include any function_call whose name is in registry_functions and not in TRANSFORMS/PRIMITIVE_SERIES
    - Also include bbands_property and macd_property nodes as their implicit indicators
    - Spec format: name(p1,p2,...) using only literal integer parameters present in the call
    - De-duplicated, sorted
    """
    basic: Set[str] = set()

    def add_spec(name: str, params: List[Any]):
        nm = (name or '').lower()
        if nm in TRANSFORMS or nm in PRIMITIVE_SERIES:
            return
        if nm not in registry_functions:
            return
        ints = _extract_ints_from_params(params)
        spec = f"{nm}({','.join(str(i) for i in ints)})" if ints else nm
        basic.add(spec)

    def walk(node: Any):
        if not isinstance(node, dict):
            return
        t = node.get('type')
        if t == 'function_call':
            nm = (node.get('name') or '').lower()
            params = node.get('parameters', [])
            add_spec(nm, params)
            for p in params:
                if isinstance(p, dict):
                    walk(p)
            return
        if t == 'bbands_property':
            # bbands(close, p, up, dn).property → include bb_* with (period, nbdev)
            prop = (node.get('property') or '').lower()
            params = node.get('parameters', [])
            if prop in ('upper','lower','middle'):
                # Map to simple bb function names
                name = {'upper':'bb_upper','lower':'bb_lower','middle':'bb_middle'}[prop]
                add_spec(name, params)
            for p in params:
                if isinstance(p, dict):
                    walk(p)
            return
        if t == 'macd_property':
            # macd property access → include the specific macd component with (fast,slow,signal)
            prop = (node.get('property') or '').lower()
            params = node.get('parameters', [])
            name = 'macd' if prop == 'macd' else ('macd_signal' if prop == 'signal' else ('macd_hist' if prop == 'histogram' else None))
            if name:
                add_spec(name, params)
            for p in params:
                if isinstance(p, dict):
                    walk(p)
            return
        # Composite/logical/comparison/arithmetic: traverse typical fields and parameters
        for k in ('left','right','left1','left2','condition','then','else'):
            if k in node and isinstance(node[k], dict):
                walk(node[k])
        if 'parameters' in node:
            for p in node['parameters']:
                if isinstance(p, dict):
                    walk(p)

    walk(ast_node)
    return sorted(basic) 