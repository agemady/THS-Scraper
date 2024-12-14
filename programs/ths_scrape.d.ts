export interface Coordinates {
    lat: number;
    lon: number;
}

export interface Location {
    name: string;
    slug: string;
    admin1Name: string;
    admin1Code: string;
    admin1Slug: string;
    admin2Code: string;
    admin2Name: string;
    admin2Slug: string;
    countryName: string;
    countryCode: string;
    countrySlug: string;
    countryIso3Code: string;
    continent: string;
    continentName: string;
    continentSlug: string;
    coordinates: Coordinates;
}

export interface ProfilePhoto {
    id: string;
    publicId: string;
}

export interface User {
    id: string;
    firstName: string;
    joinedDate: Date;
    expiryDate: string;
    profilePhoto: ProfilePhoto;
    isReferred: bool;
    referredCount: number;
    membershipTier: string;
}

export interface Photo {
    id: string;
    publicId: string;
}

export interface Animal {
    name: string;
    slug: string;
}

export interface Pet {
    photos: Photo[];
    yearOfBirth: number;
    breed: string;
    name: string;
    animal: Animal;
}

export interface Photo {
    id: string;
    publicId: string;
}

export interface Assignment {
    id: string;
    startDate: string;
    endDate: string;
    numberOfApplicants: number;
    durationInDays: number;
    lastModified: Date;
    isReviewing: bool;
    isApproximateDates: bool;
    isConfirmed: bool;
}

export interface Amenities {
    bedTypes: string[];
    hasBedding: bool;
    storageTypes: string[];
    hasAirConditioning: bool;
    heatingTypes: string[];
    wifiType: string;
    workspaceTypes: string[];
    hasSofa: bool;
    hasDiningArea: bool;
    tvTypes: string[];
    stoveType: string;
    hasOven: bool;
    hasMicrowave: bool;
    hasCoffeeMaker: bool;
    hasToaster: bool;
    hasKettle: bool;
    hasFridge: bool;
    hasFreezer: bool;
    hasCookingBasics: bool;
    hasDishwasher: bool;
    hasBlender: bool;
    hasBath: bool;
    hasShower: bool;
    hasShampoo: bool;
    hasBathroomEssentials: bool;
    hasGarden: bool;
    hasPatio: bool;
    hasBarbecue: bool;
    hasOutdoorDiningArea: bool;
    hasSecurityCameras: bool;
    hasFirstAidKit: bool;
    hasFireAlarm: bool;
    hasCarbonMonoxideAlarm: bool;
    parkingType: string;
    hasWasher: bool;
    hasDryer: bool;
    hasVacuum: bool;
    hasIron: bool;
}

export interface THS_ListingDetails {
    id: string;
    location: Location;
    user: User;
    status: string;
    title: string;
    introduction: string;
    features: string;
    responsibilities: string;
    indexedDate: Date;
    localAttractions: string[];
    pets: Pet[];
    photos: Photo[];
    assignments: Assignment[];
    disabledAccess: bool;
    homeType: string;
    familyFriendly: bool;
    amenities: Amenities;
    isAccessibleByPublicTransport: bool;
}