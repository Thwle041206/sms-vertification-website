'''
Key features of this implementation:

ProjectSchema:

Validates project name (disallows special characters)
Ensures area code is 3-4 digits if provided
Sets default values for created_at, api_calls, and updated_at
Includes example schema for documentation
Project Class Methods:

create_project: Creates new project with timestamps
get_project_by_id: Retrieves single project
get_user_projects: Gets all projects for a user (sorted by creation date)
update_project: General update method for project details
increment_api_calls: Tracks API usage per project
set_default_service/country: Specialized setters for common updates
delete_project: Removes project permanently
search_projects: Full-text search within user's projects
Usage Examples:
# Create a new project
project_data = {
    "user_id": "507f1f77bcf86cd799439011",
    "name": "User Verification",
    "default_country": "507f1f77bcf86cd799439012",
    "default_service": "507f1f77bcf86cd799439013"
}
project_id = Project.create_project(project_data)

# Get user's projects
user_projects = Project.get_user_projects("507f1f77bcf86cd799439011")

# Update default service
Project.set_default_service(project_id, "607f1f77bcf86cd799439014")

# Track API usage
Project.increment_api_calls(project_id)
'''

from typing import Optional, List
from bson import ObjectId
from pydantic import BaseModel, Field, validator
from datetime import datetime
from app.config.database import db

class ProjectSchema(BaseModel):
    id: Optional[str] = Field(None, alias='_id')
    user_id: str
    name: str = Field(..., min_length=2, max_length=100)
    description: str = Field(default="", max_length=500)
    default_country: str
    default_service: str
    area_code: Optional[str] = Field(None, pattern=r'^\d{3,4}$')
    created_at: datetime = Field(default_factory=datetime.now)
    api_calls: int = Field(default=0, ge=0)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "name": "My Verification Project",
                "description": "Project for user verification flows",
                "default_country": "507f1f77bcf86cd799439012",
                "default_service": "507f1f77bcf86cd799439013",
                "area_code": "800"
            }
        }

    @validator('name')
    def validate_name(cls, v):
        if any(char in v for char in '\\/*?"<>|'):
            raise ValueError('Project name contains invalid characters')
        return v

class Project:
    collection = db['projects']

    @staticmethod
    def create_project(project_data: dict) -> ProjectSchema:
        """Create a new project and return the created project
        Args:
            project_data: Dictionary containing project data
        Returns:
            ProjectSchema of the created project
        """
        project_data['created_at'] = datetime.now()
        project_data['updated_at'] = datetime.now()
        result = Project.collection.insert_one(project_data)
        created_project = Project.collection.find_one({'_id': result.inserted_id})
        return ProjectSchema(**created_project)

    @staticmethod
    def get_project_by_id(project_id: str) -> Optional[ProjectSchema]:
        """Get project by ID
        Args:
            project_id: The project's MongoDB ObjectId as string
        Returns:
            ProjectSchema if found, None otherwise
        Raises:
            ValueError: If project_id is invalid
        """
        try:
            project = Project.collection.find_one({'_id': ObjectId(project_id)})
            return ProjectSchema(**project) if project else None
        except Exception as e:
            raise ValueError(f"Invalid project ID: {project_id}") from e

    @staticmethod
    async def get_user_projects(user_id: ObjectId) -> List[ProjectSchema]:
        """Get all projects for a user sorted by creation date (newest first)
        Args:
            user_id: The user's MongoDB ObjectId
        Returns:
            List of ProjectSchema objects
        Raises:
            ValueError: If user_id is invalid
        """
        try:
            cursor = Project.collection.find(
                {'user_id': user_id}
            ).sort('created_at', -1)
            projects = []
            async for p in cursor:
                projects.append(ProjectSchema(**p))
            return projects
        except Exception as e:
            raise ValueError(f"Invalid user ID: {user_id}") from e

    @staticmethod
    def update_project(project_id: str, update_data: dict) -> bool:
        """Update project information"""
        update_data['updated_at'] = datetime.now()
        result = Project.collection.update_one(
            {'_id': ObjectId(project_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0

    @staticmethod
    def increment_api_calls(project_id: str, increment: int = 1) -> bool:
        """Increment the API call counter for a project"""
        result = Project.collection.update_one(
            {'_id': ObjectId(project_id)},
            {
                '$inc': {'api_calls': increment},
                '$set': {'updated_at': datetime.now()}
            }
        )
        return result.modified_count > 0

    @staticmethod
    def set_default_service(project_id: str, service_id: str) -> bool:
        """Set the default service for a project"""
        result = Project.collection.update_one(
            {'_id': ObjectId(project_id)},
            {
                '$set': {
                    'default_service': ObjectId(service_id),
                    'updated_at': datetime.now()
                }
            }
        )
        return result.modified_count > 0

    @staticmethod
    def set_default_country(project_id: str, country_id: str) -> bool:
        """Set the default country for a project"""
        result = Project.collection.update_one(
            {'_id': ObjectId(project_id)},
            {
                '$set': {
                    'default_country': ObjectId(country_id),
                    'updated_at': datetime.now()
                }
            }
        )
        return result.modified_count > 0

    @staticmethod
    def delete_project(project_id: str) -> bool:
        """Delete a project"""
        result = Project.collection.delete_one({'_id': ObjectId(project_id)})
        return result.deleted_count > 0

    @staticmethod
    def search_projects(user_id: str, query: str, limit: int = 10) -> List[ProjectSchema]:
        """Search projects by name or description with pagination
        Args:
            user_id: The user's MongoDB ObjectId as string
            query: Search term
            limit: Maximum number of results to return
        Returns:
            List of matching ProjectSchema objects
        """
        pipeline = [
            {'$match': {
                'user_id': ObjectId(user_id),
                '$or': [
                    {'name': {'$regex': query, '$options': 'i'}},
                    {'description': {'$regex': query, '$options': 'i'}}
                ]
            }},
            {'$limit': limit},
            {'$sort': {'created_at': -1}}
        ]
        results = Project.collection.aggregate(pipeline)
        return [ProjectSchema(**doc) for doc in results]
