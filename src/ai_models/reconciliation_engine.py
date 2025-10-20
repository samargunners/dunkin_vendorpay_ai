"""
Financial Reconciliation Engine

This module handles the matching of bank/credit card statements with business transactions
to provide accurate financial reconciliation and cash flow tracking.
"""

import re
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
from difflib import SequenceMatcher
import pandas as pd

from ..core.supabase_manager import SupabaseManager, TransactionManager

class ReconciliationEngine:
    """Main reconciliation engine that matches transactions"""
    
    def __init__(self, supabase_manager: SupabaseManager):
        self.supabase_manager = supabase_manager
        self.transaction_manager = TransactionManager(supabase_manager)
        
        # Matching algorithms
        self.exact_matcher = ExactMatcher()
        self.fuzzy_matcher = FuzzyMatcher()
        self.amount_matcher = AmountMatcher()
        self.date_matcher = DateMatcher()
    
    async def run_reconciliation(self, account_id: Optional[str] = None, 
                               date_range: Optional[Tuple[date, date]] = None) -> Dict[str, Any]:
        """Run the complete reconciliation process"""
        try:
            # Get unreconciled transactions
            unreconciled = await self.transaction_manager.get_unreconciled_transactions(account_id)
            
            statement_transactions = unreconciled['statements']
            outgoing_transactions = unreconciled['outgoing']
            incoming_transactions = unreconciled['incoming']
            
            results = {
                'exact_matches': [],
                'fuzzy_matches': [],
                'amount_matches': [],
                'date_matches': [],
                'unmatched_statements': [],
                'unmatched_business': [],
                'reconciliation_summary': {}
            }
            
            # Filter by date range if provided
            if date_range:
                statement_transactions = self._filter_by_date(statement_transactions, date_range)
                outgoing_transactions = self._filter_by_date(outgoing_transactions, date_range)
                incoming_transactions = self._filter_by_date(incoming_transactions, date_range)
            
            # Run matching algorithms in order of confidence
            await self._run_exact_matching(statement_transactions, outgoing_transactions, incoming_transactions, results)
            await self._run_fuzzy_matching(statement_transactions, outgoing_transactions, incoming_transactions, results)
            await self._run_amount_matching(statement_transactions, outgoing_transactions, incoming_transactions, results)
            await self._run_date_matching(statement_transactions, outgoing_transactions, incoming_transactions, results)
            
            # Generate summary
            results['reconciliation_summary'] = self._generate_summary(results)
            
            return results
            
        except Exception as e:
            raise Exception(f"Error running reconciliation: {str(e)}")
    
    async def _run_exact_matching(self, statements: List[Dict], outgoing: List[Dict], 
                                incoming: List[Dict], results: Dict[str, Any]):
        """Run exact matching algorithm"""
        matched_statements = set()
        matched_business = set()
        
        # Match outgoing transactions
        for stmt in statements:
            if stmt['id'] in matched_statements:
                continue
                
            for business_trans in outgoing:
                if business_trans['id'] in matched_business:
                    continue
                
                if self.exact_matcher.is_match(stmt, business_trans, 'outgoing'):
                    match = {
                        'statement_transaction': stmt,
                        'business_transaction': business_trans,
                        'business_transaction_type': 'outgoing',
                        'confidence_score': 1.0,
                        'match_type': 'exact'
                    }
                    results['exact_matches'].append(match)
                    matched_statements.add(stmt['id'])
                    matched_business.add(business_trans['id'])
                    
                    # Create reconciliation record
                    await self._create_reconciliation_record(match)
                    break
        
        # Match incoming transactions
        for stmt in statements:
            if stmt['id'] in matched_statements:
                continue
                
            for business_trans in incoming:
                if business_trans['id'] in matched_business:
                    continue
                
                if self.exact_matcher.is_match(stmt, business_trans, 'incoming'):
                    match = {
                        'statement_transaction': stmt,
                        'business_transaction': business_trans,
                        'business_transaction_type': 'incoming',
                        'confidence_score': 1.0,
                        'match_type': 'exact'
                    }
                    results['exact_matches'].append(match)
                    matched_statements.add(stmt['id'])
                    matched_business.add(business_trans['id'])
                    
                    # Create reconciliation record
                    await self._create_reconciliation_record(match)
                    break
    
    async def _run_fuzzy_matching(self, statements: List[Dict], outgoing: List[Dict], 
                                incoming: List[Dict], results: Dict[str, Any]):
        """Run fuzzy matching algorithm for already matched transactions"""
        # Only process transactions not already exactly matched
        matched_stmt_ids = {match['statement_transaction']['id'] for match in results['exact_matches']}
        matched_business_ids = {match['business_transaction']['id'] for match in results['exact_matches']}
        
        available_statements = [s for s in statements if s['id'] not in matched_stmt_ids]
        available_outgoing = [o for o in outgoing if o['id'] not in matched_business_ids]
        available_incoming = [i for i in incoming if i['id'] not in matched_business_ids]
        
        # Implementation similar to exact matching but with fuzzy logic
        # ... (implement fuzzy matching logic)
    
    async def _run_amount_matching(self, statements: List[Dict], outgoing: List[Dict], 
                                 incoming: List[Dict], results: Dict[str, Any]):
        """Run amount-based matching"""
        # Implementation for amount matching
        pass
    
    async def _run_date_matching(self, statements: List[Dict], outgoing: List[Dict], 
                               incoming: List[Dict], results: Dict[str, Any]):
        """Run date-proximity matching"""
        # Implementation for date matching
        pass
    
    async def _create_reconciliation_record(self, match: Dict[str, Any]):
        """Create a reconciliation record in the database"""
        try:
            reconciliation_data = {
                'statement_transaction_id': match['statement_transaction']['id'],
                'business_transaction_id': match['business_transaction']['id'],
                'business_transaction_type': match['business_transaction_type'],
                'match_type': match['match_type'],
                'confidence_score': match['confidence_score'],
                'reconciled_by': 'system',  # Will be user ID when manual
            }
            
            await self.transaction_manager.create_reconciliation(reconciliation_data)
            
        except Exception as e:
            print(f"Warning: Could not create reconciliation record: {str(e)}")
    
    def _filter_by_date(self, transactions: List[Dict], date_range: Tuple[date, date]) -> List[Dict]:
        """Filter transactions by date range"""
        start_date, end_date = date_range
        filtered = []
        
        for trans in transactions:
            trans_date_str = trans.get('transaction_date')
            if trans_date_str:
                try:
                    trans_date = datetime.fromisoformat(trans_date_str).date()
                    if start_date <= trans_date <= end_date:
                        filtered.append(trans)
                except:
                    continue
        
        return filtered
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate reconciliation summary statistics"""
        total_matches = (len(results['exact_matches']) + 
                        len(results['fuzzy_matches']) + 
                        len(results['amount_matches']) + 
                        len(results['date_matches']))
        
        return {
            'total_matches_found': total_matches,
            'exact_matches': len(results['exact_matches']),
            'fuzzy_matches': len(results['fuzzy_matches']),
            'amount_matches': len(results['amount_matches']),
            'date_matches': len(results['date_matches']),
            'unmatched_statements': len(results['unmatched_statements']),
            'unmatched_business_transactions': len(results['unmatched_business']),
            'reconciliation_rate': total_matches / (total_matches + len(results['unmatched_statements'])) if total_matches > 0 else 0
        }

class ExactMatcher:
    """Handles exact transaction matching"""
    
    def is_match(self, statement_trans: Dict[str, Any], business_trans: Dict[str, Any], 
                 business_type: str) -> bool:
        """Check if transactions are an exact match"""
        try:
            # Amount must match exactly
            stmt_amount = abs(float(statement_trans.get('amount', 0)))
            business_amount = float(business_trans.get('amount', 0))
            
            if abs(stmt_amount - business_amount) > 0.01:  # Allow for small rounding differences
                return False
            
            # Date must be within reasonable range (same day or 1-2 business days difference)
            stmt_date = self._parse_date(statement_trans.get('transaction_date'))
            business_date = self._parse_date(business_trans.get('transaction_date'))
            
            if not stmt_date or not business_date:
                return False
            
            date_diff = abs((stmt_date - business_date).days)
            if date_diff > 3:  # Allow up to 3 days difference for processing delays
                return False
            
            # For outgoing transactions, statement should be debit
            if business_type == 'outgoing':
                if statement_trans.get('transaction_type', '').lower() != 'debit':
                    return False
            
            # For incoming transactions, statement should be credit
            if business_type == 'incoming':
                if statement_trans.get('transaction_type', '').lower() != 'credit':
                    return False
            
            return True
            
        except Exception as e:
            return False
    
    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse date string to date object"""
        if not date_str:
            return None
            
        try:
            if isinstance(date_str, str):
                return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
            return date_str
        except:
            return None

class FuzzyMatcher:
    """Handles fuzzy transaction matching using text similarity"""
    
    def __init__(self, similarity_threshold: float = 0.8):
        self.similarity_threshold = similarity_threshold
    
    def is_match(self, statement_trans: Dict[str, Any], business_trans: Dict[str, Any], 
                 business_type: str) -> Tuple[bool, float]:
        """Check if transactions are a fuzzy match and return confidence score"""
        try:
            # Amount must be close (within 5%)
            stmt_amount = abs(float(statement_trans.get('amount', 0)))
            business_amount = float(business_trans.get('amount', 0))
            
            amount_diff_pct = abs(stmt_amount - business_amount) / max(stmt_amount, business_amount)
            if amount_diff_pct > 0.05:
                return False, 0.0
            
            # Date must be within reasonable range
            stmt_date = self._parse_date(statement_trans.get('transaction_date'))
            business_date = self._parse_date(business_trans.get('transaction_date'))
            
            if not stmt_date or not business_date:
                return False, 0.0
            
            date_diff = abs((stmt_date - business_date).days)
            if date_diff > 7:  # Allow up to 7 days for fuzzy matching
                return False, 0.0
            
            # Text similarity scoring
            stmt_desc = self._clean_description(statement_trans.get('description', ''))
            business_desc = self._clean_description(business_trans.get('description', ''))
            
            # Also check vendor name if available
            vendor_name = business_trans.get('vendor_name', '')
            if vendor_name:
                vendor_similarity = self._calculate_similarity(stmt_desc, self._clean_description(vendor_name))
            else:
                vendor_similarity = 0.0
            
            desc_similarity = self._calculate_similarity(stmt_desc, business_desc)
            
            # Use the higher similarity score
            text_similarity = max(desc_similarity, vendor_similarity)
            
            # Calculate overall confidence score
            amount_score = 1.0 - amount_diff_pct  # Higher score for closer amounts
            date_score = max(0.0, 1.0 - (date_diff / 7.0))  # Higher score for closer dates
            text_score = text_similarity
            
            # Weighted average
            confidence = (amount_score * 0.4 + date_score * 0.2 + text_score * 0.4)
            
            is_match = confidence >= self.similarity_threshold
            return is_match, confidence
            
        except Exception as e:
            return False, 0.0
    
    def _clean_description(self, description: str) -> str:
        """Clean and normalize description text for comparison"""
        if not description:
            return ""
        
        # Convert to lowercase
        cleaned = description.lower()
        
        # Remove common banking terms
        banking_terms = ['debit', 'credit', 'purchase', 'payment', 'transfer', 'withdrawal']
        for term in banking_terms:
            cleaned = cleaned.replace(term, '')
        
        # Remove special characters and extra spaces
        cleaned = re.sub(r'[^a-z0-9\s]', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using SequenceMatcher"""
        if not text1 or not text2:
            return 0.0
        
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse date string to date object"""
        if not date_str:
            return None
            
        try:
            if isinstance(date_str, str):
                return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
            return date_str
        except:
            return None

class AmountMatcher:
    """Handles amount-based matching for transactions with different dates"""
    
    def __init__(self, amount_tolerance: float = 0.01):
        self.amount_tolerance = amount_tolerance
    
    def find_matches(self, statements: List[Dict], business_transactions: List[Dict], 
                    business_type: str) -> List[Tuple[Dict, Dict, float]]:
        """Find transactions that match by amount"""
        matches = []
        
        for stmt in statements:
            stmt_amount = abs(float(stmt.get('amount', 0)))
            
            for business_trans in business_transactions:
                business_amount = float(business_trans.get('amount', 0))
                
                # Check amount match
                if abs(stmt_amount - business_amount) <= self.amount_tolerance:
                    # Check transaction type alignment
                    if business_type == 'outgoing' and stmt.get('transaction_type', '').lower() != 'debit':
                        continue
                    if business_type == 'incoming' and stmt.get('transaction_type', '').lower() != 'credit':
                        continue
                    
                    # Calculate confidence based on how close the amounts are
                    amount_diff = abs(stmt_amount - business_amount)
                    confidence = 1.0 - (amount_diff / max(stmt_amount, business_amount))
                    
                    matches.append((stmt, business_trans, confidence))
        
        # Sort by confidence and return top matches
        matches.sort(key=lambda x: x[2], reverse=True)
        return matches

class DateMatcher:
    """Handles date-based matching for transactions that occur on the same date"""
    
    def __init__(self, date_tolerance_days: int = 1):
        self.date_tolerance_days = date_tolerance_days
    
    def find_matches(self, statements: List[Dict], business_transactions: List[Dict], 
                    business_type: str) -> List[Tuple[Dict, Dict, float]]:
        """Find transactions that match by date proximity"""
        matches = []
        
        for stmt in statements:
            stmt_date = self._parse_date(stmt.get('transaction_date'))
            if not stmt_date:
                continue
            
            for business_trans in business_transactions:
                business_date = self._parse_date(business_trans.get('transaction_date'))
                if not business_date:
                    continue
                
                # Check date proximity
                date_diff = abs((stmt_date - business_date).days)
                if date_diff <= self.date_tolerance_days:
                    # Check transaction type alignment
                    if business_type == 'outgoing' and stmt.get('transaction_type', '').lower() != 'debit':
                        continue
                    if business_type == 'incoming' and stmt.get('transaction_type', '').lower() != 'credit':
                        continue
                    
                    # Calculate confidence based on date proximity
                    confidence = 1.0 - (date_diff / (self.date_tolerance_days + 1))
                    
                    matches.append((stmt, business_trans, confidence))
        
        # Sort by confidence and return top matches
        matches.sort(key=lambda x: x[2], reverse=True)
        return matches
    
    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse date string to date object"""
        if not date_str:
            return None
            
        try:
            if isinstance(date_str, str):
                return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
            return date_str
        except:
            return None

class CashFlowAnalyzer:
    """Analyzes cash flow patterns and generates insights"""
    
    def __init__(self, supabase_manager: SupabaseManager):
        self.supabase_manager = supabase_manager
    
    async def generate_cash_flow_report(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate comprehensive cash flow report"""
        try:
            # This would query the database for reconciled transactions in the date range
            # and generate insights about money flow patterns
            
            report = {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'summary': {
                    'total_income': 0.0,
                    'total_expenses': 0.0,
                    'net_cash_flow': 0.0
                },
                'income_breakdown': {
                    'sales_revenue': 0.0,
                    'card_payments': 0.0,
                    'cash_payments': 0.0,
                    'gift_card_payments': 0.0
                },
                'expense_breakdown': {
                    'vendor_payments': 0.0,
                    'royalty_payments': 0.0,
                    'utilities': 0.0,
                    'other': 0.0
                },
                'reconciliation_status': {
                    'reconciled_percentage': 0.0,
                    'unreconciled_transactions': 0,
                    'disputed_transactions': 0
                },
                'trends': {
                    'daily_averages': {},
                    'payment_method_distribution': {},
                    'vendor_spending_patterns': {}
                }
            }
            
            # Implementation would fetch and analyze actual data
            return report
            
        except Exception as e:
            raise Exception(f"Error generating cash flow report: {str(e)}")