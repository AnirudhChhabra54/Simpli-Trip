import pandas as pd
from services.ollama_service import ollama_service
from utils.logger import logger

class DataEnrichmentService:
    """
    Use AI to enhance and enrich destination data
    """
    
    def __init__(self):
        self.ollama = ollama_service
    
    def enrich_destination_descriptions(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Use AI to generate engaging descriptions for destinations
        """
        enriched_data = []
        
        for _, row in df.iterrows():
            enriched_row = row.to_dict()
            
            # Generate better description if needed
            if not row['description'] or len(row['description']) < 50:
                prompt = f"""Create an engaging 2-3 sentence description for {row['destination_name']} in {row['state']} 
                that highlights its {row['category']} appeal and key attractions: {row.get('popular_attractions', '')}"""
                
                try:
                    new_description = self.ollama.generate(prompt, max_tokens=100)
                    enriched_row['description'] = new_description.strip()
                except Exception as e:
                    logger.error(f"Error generating description for {row['destination_name']}: {e}")
            
            # Generate travel tips
            if not row.get('travel_tips'):
                tips_prompt = f"""Generate 3 practical travel tips for visiting {row['destination_name']} 
                in {row['best_time_visit']} for {row.get('ideal_duration', '3-4 days')}"""
                
                try:
                    tips = self.ollama.generate(tips_prompt, max_tokens=80)
                    enriched_row['travel_tips'] = tips.strip()
                except Exception as e:
                    logger.error(f"Error generating tips for {row['destination_name']}: {e}")
            
            enriched_data.append(enriched_row)
        
        return pd.DataFrame(enriched_data)
    
    def categorize_by_season(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add seasonal categorization to destinations
        """
        season_mapping = {
            '12,1,2': 'Winter',
            '3,4,5': 'Summer', 
            '6,7,8,9': 'Monsoon',
            '10,11': 'Autumn'
        }
        
        df['best_season'] = df['best_months'].map(
            lambda x: next((season for months, season in season_mapping.items() 
                           if any(month in x.split(',') for month in months.split(','))), 'Year-round')
        )
        
        return df

# Create global instance  
data_enrichment_service = DataEnrichmentService()