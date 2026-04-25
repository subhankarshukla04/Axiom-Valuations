"""
Batch valuation script - Run valuations for all companies in database
Uses centralized ValuationService for consistency.
"""
import logging
from valuation_service import ValuationService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_valuations.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_batch_valuations(db_filename='valuations.db'):
    """
    Run valuations for all companies using centralized ValuationService.
    Eliminates code duplication and ensures consistency.
    """
    logger.info(f"Starting batch valuation process for database: {db_filename}")
    
    # Initialize service
    service = ValuationService(db_filename)
    
    # Run batch valuation using service
    summary = service.batch_valuate_all()
    
    # Display results
    print("\n" + "=" * 80)
    print("📊 BATCH VALUATION SUMMARY")
    print("=" * 80)
    print(f"✅ Successful: {summary['successful']}")
    print(f"❌ Errors: {summary['failed']}")
    print(f"📈 Total: {summary['total']}")
    
    if summary['results']:
        print("\n✨ Valuation Results:")
        for result in summary['results']:
            print(f"  • {result['company_name']}: {result['recommendation']} "
                  f"(Fair Value: ${result['fair_value']:,.0f})")
    
    if summary['errors']:
        print("\n⚠️  Errors encountered:")
        for error in summary['errors']:
            print(f"  • {error['company_name']}: {error['error']}")
    
    logger.info(f"Batch valuation complete: {summary['successful']}/{summary['total']} successful")
    print("=" * 80 + "\n")
    
    if summary['successful'] > 0:
        print("✨ Valuations complete! View results at: http://localhost:5000")
    
    return summary['successful'], summary['failed']

if __name__ == '__main__':
    run_batch_valuations()
