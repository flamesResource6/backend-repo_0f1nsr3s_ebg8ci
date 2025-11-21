"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional

# Example schemas (you can keep these for testing):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Contractor Smart Site specific schemas

class Lead(BaseModel):
    """
    Leads generated from the website (demo requests, consultations)
    Collection name: "lead"
    """
    name: str = Field(..., description="Prospect full name")
    phone: str = Field(..., description="Prospect mobile phone")
    email: Optional[EmailStr] = Field(None, description="Prospect email (optional)")
    source: str = Field(..., description="Lead source e.g. demo, consultation, calculator")
    notes: Optional[str] = Field(None, description="Any additional context from the form or chat")
    industry: Optional[str] = Field(None, description="Contractor industry e.g. roofing, plumbing")

class DemoRequest(BaseModel):
    """
    Requests to trigger the AI demo SMS/chat simulation
    Collection name: "demorequest"
    """
    name: str = Field(..., description="Requester name")
    phone: str = Field(..., description="Requester phone")
    sample_intent: Optional[str] = Field(None, description="Lead intent to simulate e.g. roofing quote")
