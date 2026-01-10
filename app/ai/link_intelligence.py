"""Relationship intelligence and link analysis."""
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models import Category, Group, Customer, Subscription, Link
from app.models.link import EntityType
from app.ai.provider import AIProvider
from difflib import SequenceMatcher
import re


def extract_domain(email: str) -> str:
    """Extract domain from email address."""
    if not email or '@' not in email:
        return ""
    return email.split('@')[1].lower()


def calculate_name_similarity(name1: str, name2: str) -> float:
    """Calculate similarity between two names."""
    if not name1 or not name2:
        return 0.0
    return SequenceMatcher(None, name1.lower(), name2.lower()).ratio()


def extract_keywords(text: str) -> set:
    """Extract keywords from text."""
    if not text:
        return set()
    # Simple keyword extraction - lowercase, remove punctuation, split
    words = re.findall(r'\w+', text.lower())
    # Filter out common words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    return {w for w in words if len(w) > 2 and w not in stop_words}


class LinkAnalyzer:
    """Analyzer for discovering relationships between entities."""
    
    def __init__(self, db: Session, ai_provider: AIProvider):
        self.db = db
        self.ai_provider = ai_provider
    
    def analyze_customer_links(self) -> List[Dict[str, Any]]:
        """Find potential links between customers."""
        links = []
        customers = self.db.query(Customer).all()
        
        for i, customer1 in enumerate(customers):
            for customer2 in customers[i+1:]:
                confidence, evidence = self._analyze_customer_pair(customer1, customer2)
                if confidence > 0.15:  # Lowered threshold for better detection
                    links.append({
                        'source_type': EntityType.CUSTOMER,
                        'source_id': customer1.id,
                        'target_type': EntityType.CUSTOMER,
                        'target_id': customer2.id,
                        'confidence': confidence,
                        'evidence_text': evidence
                    })
        
        return links
    
    def _analyze_customer_pair(self, c1: Customer, c2: Customer) -> Tuple[float, str]:
        """Analyze a pair of customers for potential links."""
        evidence_parts = []
        confidence = 0.0
        
        # Same email domain
        if c1.email and c2.email:
            domain1 = extract_domain(c1.email)
            domain2 = extract_domain(c2.email)
            if domain1 and domain2 and domain1 == domain2:
                confidence += 0.4
                evidence_parts.append(f"Same email domain: {domain1}")
        
        # Similar names
        name_sim = calculate_name_similarity(c1.name, c2.name)
        if name_sim > 0.6:  # Lowered threshold
            confidence += 0.3 * name_sim
            evidence_parts.append(f"Similar names (similarity: {name_sim:.2f})")
        
        # Same phone
        if c1.phone and c2.phone and c1.phone == c2.phone:
            confidence += 0.5
            evidence_parts.append("Same phone number")
        
        # Same country
        if c1.country and c2.country and c1.country == c2.country:
            confidence += 0.15
            evidence_parts.append(f"Same country: {c1.country}")
        
        # Shared tags
        if c1.tags and c2.tags:
            tags1 = set(t.strip().lower() for t in c1.tags.split(','))
            tags2 = set(t.strip().lower() for t in c2.tags.split(','))
            shared_tags = tags1 & tags2
            if shared_tags:
                confidence += 0.2 + (0.05 * len(shared_tags))  # More shared tags = higher confidence
                evidence_parts.append(f"Shared tags: {', '.join(shared_tags)}")
        
        # Same category (weaker signal but still relevant)
        if c1.category_id == c2.category_id:
            confidence += 0.1
            evidence_parts.append(f"Same category")
        
        # Same group (strong signal)
        if c1.group_id and c2.group_id and c1.group_id == c2.group_id:
            confidence += 0.3
            evidence_parts.append(f"Same group")
        
        # Cap confidence at 1.0
        confidence = min(confidence, 1.0)
        
        return confidence, '; '.join(evidence_parts) if evidence_parts else "No strong evidence"
    
    def analyze_subscription_links(self) -> List[Dict[str, Any]]:
        """Find potential links between subscriptions."""
        links = []
        subscriptions = self.db.query(Subscription).all()
        
        for i, sub1 in enumerate(subscriptions):
            for sub2 in subscriptions[i+1:]:
                # Can link same or different customers
                confidence, evidence = self._analyze_subscription_pair(sub1, sub2)
                if confidence > 0.2:  # Lowered threshold
                    links.append({
                        'source_type': EntityType.SUBSCRIPTION,
                        'source_id': sub1.id,
                        'target_type': EntityType.SUBSCRIPTION,
                        'target_id': sub2.id,
                        'confidence': confidence,
                        'evidence_text': evidence
                    })
        
        return links
    
    def _analyze_subscription_pair(self, s1: Subscription, s2: Subscription) -> Tuple[float, str]:
        """Analyze a pair of subscriptions for potential links."""
        evidence_parts = []
        confidence = 0.0
        
        # Same vendor
        if s1.vendor_name.lower() == s2.vendor_name.lower():
            confidence += 0.4
            evidence_parts.append(f"Same vendor: {s1.vendor_name}")
            
            # Same plan within same vendor
            if s1.plan_name and s2.plan_name and s1.plan_name.lower() == s2.plan_name.lower():
                confidence += 0.2
                evidence_parts.append(f"Same plan: {s1.plan_name}")
        
        # Similar costs and billing cycles (bulk purchase indicator)
        if s1.cost == s2.cost and s1.billing_cycle == s2.billing_cycle:
            confidence += 0.15
            evidence_parts.append(f"Same pricing: {s1.cost} {s1.currency}/{s1.billing_cycle.value}")
        
        # Same country
        if s1.country and s2.country and s1.country == s2.country:
            confidence += 0.1
            evidence_parts.append(f"Same country: {s1.country}")
        
        # Same category
        if s1.category_id == s2.category_id:
            confidence += 0.1
            evidence_parts.append(f"Same category")
        
        # Similar renewal patterns (within 7 days)
        if s1.next_renewal_date and s2.next_renewal_date:
            days_diff = abs((s1.next_renewal_date - s2.next_renewal_date).days)
            if days_diff <= 7:
                confidence += 0.15
                evidence_parts.append(f"Similar renewal dates (within {days_diff} days)")
            elif days_diff <= 30:
                confidence += 0.05
                evidence_parts.append(f"Renewal dates within same month")
        
        # Same customer (different subscriptions for same customer)
        if s1.customer_id == s2.customer_id:
            confidence += 0.2
            evidence_parts.append(f"Same customer")
        
        confidence = min(confidence, 1.0)
        
        return confidence, '; '.join(evidence_parts) if evidence_parts else "No strong evidence"
    
    def analyze_cross_category_links(self) -> List[Dict[str, Any]]:
        """Find links between customers across different categories."""
        links = []
        customers = self.db.query(Customer).all()
        
        # Group by email domain
        domain_customers = {}
        for customer in customers:
            if customer.email:
                domain = extract_domain(customer.email)
                if domain:
                    if domain not in domain_customers:
                        domain_customers[domain] = []
                    domain_customers[domain].append(customer)
        
        # Create links for customers with same domain but different categories
        for domain, customers_list in domain_customers.items():
            if len(customers_list) > 1:
                categories_in_group = {c.category_id for c in customers_list}
                if len(categories_in_group) > 1:  # Cross-category
                    for i, c1 in enumerate(customers_list):
                        for c2 in customers_list[i+1:]:
                            if c1.category_id != c2.category_id:
                                links.append({
                                    'source_type': EntityType.CUSTOMER,
                                    'source_id': c1.id,
                                    'target_type': EntityType.CUSTOMER,
                                    'target_id': c2.id,
                                    'confidence': 0.8,
                                    'evidence_text': f"Same organization domain ({domain}) across categories"
                                })
        
        return links
    
    async def refine_with_ai(self, links: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Use AI to refine confidence scores and evidence."""
        if not self.ai_provider.is_available() or not links:
            return links
        
        # For demo purposes, we'll just enhance the evidence text
        # In production, you might batch these requests
        try:
            for link in links[:5]:  # Limit to avoid too many API calls
                prompt = f"""Analyze this potential relationship:
Evidence: {link['evidence_text']}
Confidence: {link['confidence']:.2f}

Provide a brief explanation (max 50 words) of why this relationship might be meaningful."""
                
                explanation = await self.ai_provider.generate_completion(
                    prompt=prompt,
                    system_prompt="You are an expert at analyzing business relationships and subscription patterns.",
                    temperature=0.5,
                    max_tokens=100
                )
                
                link['evidence_text'] += f" | AI: {explanation}"
        except Exception:
            # If AI fails, just return the original links
            pass
        
        return links
