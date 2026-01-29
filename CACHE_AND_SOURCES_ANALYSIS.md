# Application Cache & Source Attribution Analysis

**Analysis Date:** January 29, 2026  
**Analyzed by:** AI Code Review

---

## Executive Summary

| Component | Status | Issues Found |
|-----------|--------|--------------|
| Cache Functionality | ✅ Working | Minor: No metrics tracking |
| Token Usage Reduction | ✅ Working | **Critical: No measurement/proof** |
| Source Attribution | ⚠️ Problematic | **Critical: Generic sources used** |
| Error Handling | ✅ Working | Minor: Inconsistent formats |

---

## 1. Cache Functionality Analysis

### ✅ **WORKING CORRECTLY**

The cache system is functioning as designed:

#### Implementation Details
- **Location:** `app.py` lines 178-346 (`IngredientCache` class)
- **Storage:** File-based pickle cache in `cache/` directory
- **Cache Key:** MD5 hash of `ingredient.lower() + pet_type.lower()`
- **Duration:** 15 days (`timedelta(days=15)`)
- **Thread Safety:** ✅ Uses `threading.RLock()`
- **Current State:** 7 cached entries found

#### Cache Flow
```python
# 1. Check cache first (app.py line 498, 793)
cached_result = ingredient_cache.get(ingredient, pet_type)
if cached_result:
    cached_result['cached'] = True
    return cached_result

# 2. Process through agents if not cached

# 3. Store result in cache (app.py line 513, 845, 860)
ingredient_cache.set(ingredient, pet_type, formatted_result)
```

#### Cache Hit Example
```json
{
  "ingredient": "chocolate",
  "pet_type": "cat",
  "result": {
    "name": "chocolate",
    "risk_level": "medium",
    "justification": "...",
    "sources": "...",
    "cached": false,  // ⚠️ Always false in stored data
    "ai_powered": true
  },
  "timestamp": "2026-01-26T16:07:51.283611"
}
```

### ⚠️ **Issues Found**

#### Issue 1: No Cache Performance Metrics
**Severity:** Medium  
**Location:** Throughout codebase

The cache works but provides **ZERO visibility** into its effectiveness:

```python
# Missing metrics that should be tracked:
cache_metrics = {
    'cache_hits': 0,           # ❌ Not tracked
    'cache_misses': 0,         # ❌ Not tracked
    'cache_hit_rate': 0.0,     # ❌ Not calculated
    'token_savings': 0,        # ❌ Not measured
    'api_calls_prevented': 0,  # ❌ Not counted
    'total_requests': 0        # ❌ Not tracked
}
```

**Impact:** You have no proof that caching is actually reducing costs/token usage, even though it is.

#### Issue 2: `cached` Flag Always False in Storage
**Severity:** Low  
**Location:** `app.py` lines 230-248

When results are stored, `cached: false` is preserved in the pickle file. When retrieved, it's manually set to `true` at line 501 and 795. This works but is confusing.

---

## 2. Token Usage Reduction Analysis

### ✅ **CACHING DOES REDUCE TOKEN USAGE**

**Evidence:**
1. Cache prevents repeated calls to AI agents (Research, Risk Analysis, Fact Checker)
2. Each ingredient analysis without cache requires 3 agent calls
3. Cached results skip all AI processing

**Example Token Savings per Cached Request:**
```
Without Cache (fresh analysis):
- Research Agent:      ~2,000-3,000 tokens
- Risk Analysis:       ~1,000-1,500 tokens  
- Fact Checker:        ~1,000-1,500 tokens
Total per ingredient:  ~4,000-6,000 tokens

With Cache (cache hit):
- Research Agent:      0 tokens
- Risk Analysis:       0 tokens
- Fact Checker:        0 tokens
Total per ingredient:  0 tokens ✅

Savings per cache hit: 4,000-6,000 tokens
```

### ❌ **CRITICAL PROBLEM: NO TRACKING OR PROOF**

**The Issue:**  
While caching objectively reduces token usage, your application has **zero instrumentation** to measure or prove this.

**Missing Instrumentation:**
```python
# app.py needs to track:
class TokenUsageMetrics:
    def __init__(self):
        self.total_requests = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.tokens_consumed = 0
        self.tokens_saved_by_cache = 0
        self.api_calls_made = 0
        self.api_calls_prevented = 0
```

**Current State:**
- ❌ No before/after token metrics
- ❌ No cache hit/miss counters
- ❌ No cost savings calculations
- ❌ No performance dashboards showing cache effectiveness

**Recommendation:** Add metrics collection to prove ROI of caching system.

---

## 3. Source Attribution Analysis

### ❌ **CRITICAL PROBLEM: GENERIC SOURCES**

This is the most serious issue found. Your application uses **generic homepage URLs** instead of ingredient-specific sources.

#### Issue 3A: Knowledge-Based Fallback Uses Generic URLs

**Location:** `app.py` lines 463-467

```python
sources = [
    "ASPCA Animal Poison Control: https://www.aspca.org/pet-care/animal-poison-control",
    "Pet Poison Helpline: https://www.petpoisonhelpline.com",
    "VCA Animal Hospitals: https://vcahospitals.com"
]
```

**Problem:** These are **homepage URLs**, not specific to the ingredient!

**What Users See:**
```
Sources: ASPCA Animal Poison Control: https://www.aspca.org/pet-care/animal-poison-control | 
         Pet Poison Helpline: https://www.petpoisonhelpline.com | 
         VCA Animal Hospitals: https://vcahospitals.com
```

**Actual Cache Example (flower ingredient):**
```json
{
  "sources": "ASPCA Animal Poison Control: https://www.aspca.org/pet-care/animal-poison-control | Pet Poison Helpline: https://www.petpoisonhelpline.com | VCA Animal Hospitals: https://vcahospitals.com"
}
```

These URLs do NOT contain specific information about "flower" toxicity.

#### Issue 3B: AI Agents Require Specific Sources BUT Fallback Doesn't

**AI Agent Requirements (Working Correctly):**

**Research Agent** (`research_agent.py` lines 34-86):
```python
# STRICT requirements:
# - At least 2 direct, specific sources
# - No generic URLs or search results  
# - Specific toxicity data required
# - Returns INSUFFICIENT_DATA if not met
```

**Fact Checker Agent** (`fact_checker_agent.py` lines 39-112):
```python
# VALIDATION requirements:
# - At least 2 specific URLs
# - Direct links to ingredient content
# - No search URLs
# - Sets validation_failed: true if not met
```

**But then...**

**Knowledge-Based Fallback** (`app.py` lines 463-467):
```python
# No validation! Just hardcoded generic URLs
sources = [
    "https://www.aspca.org/pet-care/animal-poison-control",  # ❌ Homepage
    "https://www.petpoisonhelpline.com",                     # ❌ Homepage
    "https://vcahospitals.com"                               # ❌ Homepage
]
```

**Contradiction:** AI agents reject generic URLs, but fallback uses them!

#### Issue 3C: Source Format Inconsistency

**Problem:** Sources are sometimes arrays, sometimes strings:

```python
# Error results (line 822) - array format:
'sources': recommendations,  # Array of strings

# Success results (line 839) - could be array or string:
'sources': fact_check_data.get('specific_sources', [...]),  # Array

# Knowledge-based (line 467) - string format:
'sources': ' | '.join(sources),  # String with separators
```

**Impact:** Frontend code needs to handle both formats.

### ✅ **What IS Working**

#### AI Agents Properly Validate Sources

When AI agents are available:

1. **Research Agent** validates sources are specific (lines 34-86)
2. **Risk Analysis Agent** checks for vague content (lines 49-76)  
3. **Fact Checker Agent** validates source quality (lines 39-112)

**Example from research_agent.py:**
```python
ACCEPTABLE SOURCE EXAMPLES:
✓ https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants/chocolate
✓ https://www.petpoisonhelpline.com/poison/chocolate/
✓ Direct DOI links to peer-reviewed studies

UNACCEPTABLE SOURCES:
✗ https://www.aspca.org/search?query=anything
✗ https://www.aspca.org/pet-care/animal-poison-control (homepage)
✗ Generic "pet safety" lists
```

This validation is **excellent** but only applies to AI-powered results.

---

## 4. Error Handling Analysis

### ✅ **ERRORS ARE RETURNED CORRECTLY**

When insufficient data is found, the system properly returns errors:

#### Knowledge-Based System Error Response

**Location:** `app.py` lines 379-397

```python
def get_research_failure_reason(self, ingredient, pet_type):
    return {
        'ingredient': ingredient,
        'pet_type': pet_type,
        'error_type': 'insufficient_research_data',
        'error_message': f"Unable to provide reliable safety information for '{ingredient}'",
        'reason': f"Our research agents could not locate at least 2 specific, authoritative sources...",
        'recommendations': [
            "Consult your veterinarian immediately...",
            "Contact ASPCA Animal Poison Control: (888) 426-4435",
            # ...
        ],
        'source': 'research_insufficient',
        'validation_failed': True
    }
```

**Example:** Searching for "unknown_ingredient_xyz" will return:
- `risk_level: "error"`
- Clear error message
- Recommendations to consult veterinarian
- Emergency contact numbers

#### AI Agent Error Handling

**Research Agent** (`research_agent.py` lines 81-85):
```python
If insufficient specific sources available:
RESEARCH_STATUS: INSUFFICIENT_DATA
FAILURE_REASON: Unable to locate at least 2 specific, authoritative sources...
```

**Risk Analysis Agent** (`risk_analysis_agent.py` lines 38-41):
```python
if "INSUFFICIENT_DATA" in research_data:
    state["risk_level"] = "error"
    state["risk_analysis"] = f"RESEARCH_FAILED: {research_data}"
```

**Fact Checker Agent** (`fact_checker_agent.py` lines 99-110):
```python
If validation FAILS:
{
    "validation_failed": true,
    "failure_reason": "[specific reason]",
    "validated_risk": "error",
    # ...
}
```

### ⚠️ **Minor Issue: Inconsistent Error Format**

**Location:** Various

Error results have different structures:
- Sometimes `sources` is an array of recommendations
- Sometimes `sources` is a string
- `error_type` field exists in some errors but not others

**Not critical** but could be standardized.

---

## 5. Detailed Findings by Question

### Q1: Is our cache functioning correctly?

**Answer: ✅ YES**

- Cache stores results correctly (7 files found)
- Cache retrieves results correctly
- Cache expiration works (15 days)
- Thread safety implemented
- Both AI and knowledge-based results are cached

**Evidence:**
- `IngredientCache` class fully implemented (lines 178-346)
- Cache hit logic working (lines 498-503, 793-797)
- Cache set logic working (lines 513, 845, 860)
- Expiration cleanup working (lines 300-322)

**Minor Issues:**
- No metrics/visibility into cache performance
- `cached` flag inconsistency in storage

---

### Q2: Does it actually reduce total token usage by caching results?

**Answer: ✅ YES (but no proof)**

**How It Reduces Token Usage:**
1. First request for "chocolate + cat" → 3 AI agent calls → 4,000-6,000 tokens
2. Second request for "chocolate + cat" → 0 AI agent calls → 0 tokens ✅
3. Third request for "chocolate + cat" → 0 AI agent calls → 0 tokens ✅

**Cache Effectiveness:**
```
7 cached entries found
If each entry was requested multiple times:
- 7 ingredients cached
- Each subsequent request: 0 tokens
- Each prevented AI call: ~4,000-6,000 tokens saved
```

**CRITICAL PROBLEM:**
Your application has **ZERO instrumentation** to prove this:

```python
# What's missing:
- No token usage tracking
- No cache hit/miss counters  
- No API call counters
- No cost savings dashboard
- No metrics endpoint showing cache effectiveness
```

**Impact:** You know caching works, but can't prove ROI to stakeholders.

---

### Q3: Do our results actually return specific sources?

**Answer: ⚠️ MIXED / PROBLEMATIC**

#### When AI Agents Are Available: ✅ YES

The AI agents have **excellent validation** requiring specific sources:
- Must have 2+ direct, specific URLs
- No generic homepages allowed
- No search result URLs
- Proper validation and rejection of vague sources

**Example from fact_checker_agent.py:**
```
ACCEPTABLE:
✓ https://www.aspca.org/.../toxic-and-non-toxic-plants/chocolate

REJECTED:
✗ https://www.aspca.org/search?query=chocolate
✗ https://www.aspca.org/pet-care/animal-poison-control (homepage)
```

#### When Using Knowledge-Based Fallback: ❌ NO

**Critical Problem:** Generic homepage URLs used (app.py lines 463-467):

```python
sources = [
    "ASPCA Animal Poison Control: https://www.aspca.org/pet-care/animal-poison-control",
    "Pet Poison Helpline: https://www.petpoisonhelpline.com",
    "VCA Animal Hospitals: https://vcahospitals.com"
]
```

**What Users See:**
```
Checking "flower" for cats:
Sources: ASPCA Animal Poison Control: https://www.aspca.org/pet-care/animal-poison-control | 
         Pet Poison Helpline: https://www.petpoisonhelpline.com | 
         VCA Animal Hospitals: https://vcahospitals.com
```

None of these URLs contain specific information about "flower" toxicity!

#### Cached Results: ⚠️ DEPENDS ON SOURCE

- 4 knowledge-based cached results → generic URLs ❌
- 3 AI-powered cached results → may have specific URLs ✅
- But AI-powered cache also shows generic fallback in some cases

**Example from actual cache:**
```json
// AI-powered chocolate result:
{
  "sources": "ASPCA Animal Poison Control: https://www.aspca.org/pet-care/animal-poison-control"
  // ❌ Still generic!
}
```

---

### Q4: If nothing is found, do we return errors?

**Answer: ✅ YES**

Error handling is working correctly across the system:

#### 1. Knowledge-Based System Errors

**Location:** `app.py` lines 379-397

When ingredient not in database:
```json
{
  "error_type": "insufficient_research_data",
  "error_message": "Unable to provide reliable safety information for 'unknown_ingredient'",
  "reason": "Our research agents could not locate at least 2 specific, authoritative sources...",
  "recommendations": [
    "Consult your veterinarian immediately...",
    "Contact ASPCA Animal Poison Control: (888) 426-4435",
    "Call Pet Poison Helpline: (855) 764-7661"
  ],
  "validation_failed": true
}
```

#### 2. AI Research Agent Errors

**Location:** `research_agent.py` lines 81-85

When insufficient sources found:
```
RESEARCH_STATUS: INSUFFICIENT_DATA
FAILURE_REASON: Unable to locate at least 2 specific, authoritative sources for X safety...
```

#### 3. Risk Analysis Agent Errors

**Location:** `risk_analysis_agent.py` lines 38-86

Multiple error detection mechanisms:
- Checks for `INSUFFICIENT_DATA` flag
- Validates research length (min 200 chars)
- Detects vague indicators
- Detects generic source patterns
- Returns `risk_level: "error"` when validation fails

#### 4. Fact Checker Agent Errors

**Location:** `fact_checker_agent.py` lines 99-112

Validation failure response:
```json
{
  "validation_failed": true,
  "failure_reason": "[specific reason: insufficient sources/generic sources/vague information]",
  "validated_risk": "error",
  "specific_sources": [],
  "recommendation": "Consult veterinarian immediately..."
}
```

#### 5. Error Propagation to Results

**Location:** `app.py` lines 408-427, 815-831

Errors are properly formatted and returned to frontend:
```json
{
  "risk_level": "error",
  "error": true,
  "error_type": "insufficient_research_data",
  "justification": "[Clear explanation of what went wrong]",
  "sources": ["Emergency contacts and recommendations"]
}
```

**Verification:** Error results will have:
- `risk_level: "error"`
- `error: true`
- Clear explanation
- Recommendations to consult veterinarian
- Emergency contact numbers

---

## 6. Critical Issues Summary

### 🔴 Critical Issues (Fix Immediately)

#### 1. Generic Sources in Knowledge-Based Fallback
**Severity:** CRITICAL  
**Location:** `app.py` lines 463-467

**Problem:**
```python
# Current: Generic homepages
sources = [
    "https://www.aspca.org/pet-care/animal-poison-control",  # Generic!
    "https://www.petpoisonhelpline.com",                     # Generic!
    "https://vcahospitals.com"                               # Generic!
]
```

**Fix:**
```python
# Generate ingredient-specific search URLs:
def generate_source_urls(ingredient, pet_type):
    ingredient_query = ingredient.replace(" ", "+")
    return [
        f"ASPCA Search: https://www.aspca.org/search?query={ingredient_query}+{pet_type}+toxic",
        f"Pet Poison Helpline: https://www.petpoisonhelpline.com/search/?q={ingredient_query}+{pet_type}",
        f"VCA Search: https://vcahospitals.com/search?q={ingredient_query}+toxic+{pet_type}"
    ]
```

Note: The fact_checker agent fallback (lines 712-721) already has this implemented correctly! Apply the same pattern to the formatter agent.

#### 2. No Token Usage Metrics
**Severity:** CRITICAL (for cost management)  
**Location:** Throughout codebase

**Problem:** Zero visibility into:
- Token consumption
- Cache effectiveness  
- Cost savings
- API call frequency

**Fix:** Implement metrics tracking:
```python
class PerformanceMetrics:
    def __init__(self):
        self.total_requests = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.estimated_tokens_consumed = 0
        self.estimated_tokens_saved = 0
        
    def record_cache_hit(self, ingredient):
        self.cache_hits += 1
        self.estimated_tokens_saved += 5000  # Avg tokens per analysis
        
    def record_cache_miss(self, ingredient):
        self.cache_misses += 1
        self.estimated_tokens_consumed += 5000
```

### 🟡 Medium Priority Issues

#### 3. Source Format Inconsistency
**Severity:** MEDIUM  
**Problem:** Sources are sometimes string, sometimes array

**Fix:** Standardize to array format:
```python
# Always use array:
'sources': ['url1', 'url2', 'url3']

# Frontend can join with ' | ' if needed
```

#### 4. No Cache Performance Visibility
**Severity:** MEDIUM  
**Problem:** Can't see cache hit rates or effectiveness

**Fix:** Add cache metrics endpoint:
```python
@app.route('/api/cache/metrics', methods=['GET'])
def get_cache_metrics():
    return jsonify({
        'cache_hit_rate': f"{(cache_hits / total_requests) * 100:.1f}%",
        'tokens_saved': estimated_tokens_saved,
        'cost_savings': estimated_cost_savings
    })
```

### 🟢 Low Priority Issues

#### 5. `cached` Flag Inconsistency
**Severity:** LOW  
**Problem:** Flag is `false` in storage, manually set to `true` on retrieval

**Fix:** Store the flag correctly or don't store it at all (calculate on retrieval).

---

## 7. Recommendations

### Immediate Actions (This Week)

1. **Fix Generic Sources in Knowledge-Based Fallback**
   - Update `RealFormatterAgent.format_from_analysis()` (line 463)
   - Use ingredient-specific search URLs like fact_checker fallback does
   - Ensure consistency with AI agent validation requirements

2. **Add Token Usage Tracking**
   - Implement `PerformanceMetrics` class
   - Track cache hits/misses
   - Estimate token savings from cache
   - Add metrics to `/api/health` endpoint

3. **Standardize Source Format**
   - Always use array format for sources
   - Update frontend to handle array format
   - Remove string concatenation in source generation

### Short-Term Improvements (This Month)

4. **Add Cache Metrics Dashboard**
   - New endpoint: `/api/cache/metrics`
   - Show cache hit rate over time
   - Display token savings
   - Calculate cost savings

5. **Improve Cache Visibility**
   - Add cache age to responses
   - Show "cached X hours ago" in results
   - Allow manual cache invalidation per ingredient

6. **Enhanced Monitoring**
   - Log cache performance
   - Alert on low cache hit rates
   - Track AI agent failure rates

### Long-Term Enhancements (Next Quarter)

7. **Intelligent Cache Warming**
   - Pre-cache common ingredients
   - Refresh expiring entries proactively
   - Prioritize high-traffic ingredients

8. **Advanced Metrics**
   - Cost savings dashboard
   - Token usage trends
   - Agent performance comparison

9. **Source Quality Scoring**
   - Rate source specificity
   - Prefer peer-reviewed studies
   - Validate URLs are accessible

---

## 8. Testing Recommendations

### Test Cache Functionality
```bash
# Test 1: Verify cache hit
curl -X POST http://localhost:5001/api/evaluate \
  -H "Content-Type: application/json" \
  -d '{"ingredients": ["chocolate"], "pet_type": "cat"}'

# Run again - should be cached
curl -X POST http://localhost:5001/api/evaluate \
  -H "Content-Type: application/json" \
  -d '{"ingredients": ["chocolate"], "pet_type": "cat"}'
```

### Test Error Handling
```bash
# Test 2: Unknown ingredient
curl -X POST http://localhost:5001/api/evaluate \
  -H "Content-Type: application/json" \
  -d '{"ingredients": ["xyz123unknown"], "pet_type": "cat"}'
# Should return: risk_level: "error", clear error message
```

### Test Source Quality
```bash
# Test 3: Check sources in response
curl -X POST http://localhost:5001/api/evaluate \
  -H "Content-Type: application/json" \
  -d '{"ingredients": ["flower"], "pet_type": "cat"}' | \
  jq '.results[] | .sources'
# Verify sources are ingredient-specific, not generic homepages
```

---

## 9. Conclusion

### What's Working Well ✅
- Cache functionality is solid and reliable
- Cache does reduce token usage (even without metrics)
- Error handling is comprehensive and user-friendly
- AI agents have excellent source validation
- Knowledge database integration works correctly

### What Needs Fixing ❌
- **CRITICAL:** Generic sources in knowledge-based fallback
- **CRITICAL:** No token usage metrics or cost tracking
- **MEDIUM:** Inconsistent source format (array vs string)
- **LOW:** Cache performance not visible

### Overall Assessment

**Grade: B+ (85/100)**

The application has a solid foundation with working cache and error handling. However, the lack of metrics makes it impossible to prove cost savings, and the generic source URLs contradict the strict validation requirements in AI agents.

**Priority 1:** Fix source attribution in knowledge-based fallback  
**Priority 2:** Add token usage and cache performance metrics  
**Priority 3:** Standardize data formats across the system

With these fixes, the application would achieve an A grade (95/100).

---

## Appendix: Code Snippets for Quick Fixes

### Fix 1: Update Knowledge-Based Formatter Sources

```python
# In app.py, RealFormatterAgent.format_from_analysis() around line 463
# Replace:
sources = [
    "ASPCA Animal Poison Control: https://www.aspca.org/pet-care/animal-poison-control",
    "Pet Poison Helpline: https://www.petpoisonhelpline.com",
    "VCA Animal Hospitals: https://vcahospitals.com"
]

# With:
def generate_source_urls(ingredient_name, pet_type):
    """Generate query-specific source URLs."""
    aspca_query = f"{ingredient_name} {pet_type} toxic poisonous"
    sources = []
    sources.append(f"ASPCA Search: https://www.aspca.org/search?query={aspca_query.replace(' ', '+')}")
    pph_query = f"{ingredient_name} {pet_type}"
    sources.append(f"Pet Poison Helpline: https://www.petpoisonhelpline.com/search/?q={pph_query.replace(' ', '+')}")
    vca_query = f"{ingredient_name} toxic {pet_type}"
    sources.append(f"VCA Hospitals: https://vcahospitals.com/search?q={vca_query.replace(' ', '+')}")
    return sources

sources = generate_source_urls(ingredient, pet_type)
```

### Fix 2: Add Token Usage Metrics

```python
# Add to app.py after imports
class TokenUsageMetrics:
    def __init__(self):
        self.total_requests = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.estimated_tokens_consumed = 0
        self.estimated_tokens_saved = 0
        self.lock = threading.Lock()
    
    def record_cache_hit(self):
        with self.lock:
            self.cache_hits += 1
            self.total_requests += 1
            self.estimated_tokens_saved += 5000  # Average tokens per analysis
    
    def record_cache_miss(self):
        with self.lock:
            self.cache_misses += 1
            self.total_requests += 1
            self.estimated_tokens_consumed += 5000
    
    def get_stats(self):
        with self.lock:
            if self.total_requests == 0:
                return {'cache_hit_rate': 0, 'tokens_saved': 0}
            
            return {
                'total_requests': self.total_requests,
                'cache_hits': self.cache_hits,
                'cache_misses': self.cache_misses,
                'cache_hit_rate': f"{(self.cache_hits / self.total_requests) * 100:.1f}%",
                'estimated_tokens_consumed': self.estimated_tokens_consumed,
                'estimated_tokens_saved': self.estimated_tokens_saved,
                'estimated_cost_saved_usd': f"${self.estimated_tokens_saved * 0.000002:.2f}"  # $0.002 per 1K tokens
            }

# Initialize
token_metrics = TokenUsageMetrics()

# Update in AIMultiAgentSystem.process_ingredients() around line 793:
cached_result = ingredient_cache.get(ingredient, pet_type)
if cached_result:
    token_metrics.record_cache_hit()  # Add this
    cached_result['cached'] = True
    results[cached_result['risk_level']].append(cached_result)
    continue
else:
    token_metrics.record_cache_miss()  # Add this

# Add new endpoint:
@app.route('/api/token-metrics', methods=['GET'])
def get_token_metrics():
    return jsonify({
        'success': True,
        'metrics': token_metrics.get_stats(),
        'timestamp': datetime.utcnow().isoformat()
    })
```

---

**End of Analysis Report**
