// Type definitions for THS API responses

/**
 * @typedef {Object} Coordinates
 * @property {number} lat
 * @property {number} lon
 */

/**
 * @typedef {Object} Location 
 * @property {string} name
 * @property {string} slug
 * @property {string} admin1Name
 * @property {string} admin1Code
 * @property {string} admin1Slug
 * @property {string} admin2Code
 * @property {string} admin2Name
 * @property {string} admin2Slug
 * @property {string} countryName
 * @property {string} countryCode
 * @property {string} countrySlug
 * @property {string} countryIso3Code
 * @property {string} continent
 * @property {string} continentName
 * @property {string} continentSlug
 * @property {Coordinates} coordinates
 */

/**
 * @typedef {Object} ProfilePhoto
 * @property {string} id
 * @property {string} publicId
 */

/**
 * @typedef {Object} User
 * @property {string} id
 * @property {string} firstName
 * @property {Date} joinedDate
 * @property {string} expiryDate
 * @property {ProfilePhoto} profilePhoto
 * @property {boolean} isReferred
 * @property {number} referredCount
 * @property {string} membershipTier
 */

/**
 * @typedef {Object} Photo
 * @property {string} id
 * @property {string} publicId
 */

/**
 * @typedef {Object} Animal
 * @property {string} name
 * @property {string} slug
 */

/**
 * @typedef {Object} Pet
 * @property {Photo[]} photos
 * @property {number} yearOfBirth
 * @property {string} breed
 * @property {string} name
 * @property {Animal} animal
 */

/**
 * @typedef {Object} Assignment
 * @property {string} id
 * @property {string} startDate
 * @property {string} endDate
 * @property {number} numberOfApplicants
 * @property {number} durationInDays
 * @property {Date} lastModified
 * @property {boolean} isReviewing
 * @property {boolean} isApproximateDates
 * @property {boolean} isConfirmed
 */

/**
 * @typedef {Object} Amenities
 * @property {string[]} bedTypes
 * @property {boolean} hasBedding
 * @property {string[]} storageTypes
 * @property {boolean} hasAirConditioning
 * @property {string[]} heatingTypes
 * @property {string} wifiType
 * @property {string[]} workspaceTypes
 * @property {boolean} hasSofa
 * @property {boolean} hasDiningArea
 * @property {string[]} tvTypes
 * @property {string} stoveType
 * @property {boolean} hasOven
 * @property {boolean} hasMicrowave
 * @property {boolean} hasCoffeeMaker
 * @property {boolean} hasToaster
 * @property {boolean} hasKettle
 * @property {boolean} hasFridge
 * @property {boolean} hasFreezer
 * @property {boolean} hasCookingBasics
 * @property {boolean} hasDishwasher
 * @property {boolean} hasBlender
 * @property {boolean} hasBath
 * @property {boolean} hasShower
 * @property {boolean} hasShampoo
 * @property {boolean} hasBathroomEssentials
 * @property {boolean} hasGarden
 * @property {boolean} hasPatio
 * @property {boolean} hasBarbecue
 * @property {boolean} hasOutdoorDiningArea
 * @property {boolean} hasSecurityCameras
 * @property {boolean} hasFirstAidKit
 * @property {boolean} hasFireAlarm
 * @property {boolean} hasCarbonMonoxideAlarm
 * @property {string} parkingType
 * @property {boolean} hasWasher
 * @property {boolean} hasDryer
 * @property {boolean} hasVacuum
 * @property {boolean} hasIron
 */

/**
 * @typedef {Object} THS_ListingDetails
 * @property {string} id
 * @property {Location} location
 * @property {User} user
 * @property {string} status
 * @property {string} title
 * @property {string} introduction
 * @property {string} features
 * @property {string} responsibilities
 * @property {Date} indexedDate
 * @property {string[]} localAttractions
 * @property {Pet[]} pets
 * @property {Photo[]} photos
 * @property {Assignment[]} assignments
 * @property {boolean} disabledAccess
 * @property {string} homeType
 * @property {boolean} familyFriendly
 * @property {Amenities} amenities
 * @property {boolean} isAccessibleByPublicTransport
 */

/**
 * @type {Function}
 */
const cb = arguments[0];

(async function() {
    async function getData() {
        const debugOutput = true;
        let listingsTotal = 6900;
        let listingsPerPage = 100;
        let threads = 512;
        let listingIds = [];
        /**
         * @type {THS_ListingDetails[]}
         */
        let listingDetails = [];

        const reqHeaders = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Timezone-Offset": "-4",
            "Api-Key": "null",
            "Api-Version": "2021-10-26",
            "THS-Platform-Detail": "web",
            "sentry-trace": "89be5226ddea45b89427c5b0e265f0a4-8e5523de309fa2e1-0",
            "baggage": "sentry-environment=production,sentry-release=web-2606-5db7356612,sentry-public_key=d7d0029b0a63456da5e5bfd4f71cf9e2,sentry-trace_id=89be5226ddea45b89427c5b0e265f0a4,sentry-sample_rate=0.1,sentry-sampled=false",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache"
        }

        const filerObj_seattle = {
            "activeMembership": true,
            "assignments": {
                "dateFrom": new Date().toISOString().split('T')[0],
                "dateTo": "2025-12-31", 
                "confirmed": false
            },
            "geoPoint": {
                "latitude":47.6061,
                "longitude":-122.3328,
                "distance":"20km"
            }
        };
        const filterUrlStr = (JSON.stringify(filerObj_seattle)).replace(/"/g, "%22");

        async function parallel(arr, fn, mapResult = null, threads = 2) {
            const result = [];
            while (arr.length) {
                const res = await Promise.all(arr.splice(0, threads).map(x => fn(x)));
                if (typeof mapResult == 'function') {
                    result.push(res.map(mapResult));
                } else if (mapResult === null || typeof mapResult === 'undefined') {
                    result.push(res);
                }
            }
            return result.flat();
        }

        async function getTotalListingCount() {
            let response = await fetch(`https://www.trustedhousesitters.com/api/v3/search/listings/?query={%22filters%22:${filterUrlStr},%22facets%22:[%22geoBounds%22],%22sort%22:[{%22published%22:%22desc%22}],%22page%22:1,%22resultsPerPage%22:0,%22debug%22:false}`, {
                "credentials": "include",
                "headers": reqHeaders,
                "method": "GET",
                "mode": "cors"
            });
            let json = await response.json();
            console.log(json);
            if (typeof json !== 'object' || !(json.hasOwnProperty('total') && json.hasOwnProperty('facets'))) {
                return -1;
            }
            return json.total;
        }

        const fetchIds = async (idx) => {
            let response = await fetch(`https://www.trustedhousesitters.com/api/v3/search/listings/?query={%22filters%22:${filterUrlStr},%22facets%22:[],%22sort%22:[{%22function%22:{%22name%22:%22SITS_WITH_DATES_FIRST%22,%22order%22:%22asc%22}}],%22page%22:${idx + 1},%22resultsPerPage%22:${listingsPerPage},%22debug%22:false}`, {
                "credentials": "include",
                "headers": reqHeaders,
                "method": "GET",
                "mode": "cors"
            });
            if (debugOutput) console.log(`  Fetched overview info for listing index '${(idx).toString().padStart(6, ' ')}'`);
            return response.json();
        };

        let detailNum = 0;
        const fetchDetails = async (id) => {
            try {
                let response = await fetch(`https://www.trustedhousesitters.com/api/v3/search/listings/${id}/`, {
                    "credentials": "include",
                    "headers": reqHeaders,
                    "method": "GET",
                    "mode": "cors"
                });
                if (debugOutput) console.log(`  Fetched listing details for id '${id.padEnd(8, ' ')}' (#${(++detailNum).toString().padStart(6, ' ')})`);
                return response.json();
            } catch (ex) {
                if (debugOutput) console.log(`  Errored fetching listing details for id '${id.padEnd(8, ' ')}' (#${(++detailNum).toString().padStart(6, ' ')})`);
                return new Promise((resolve, _) => resolve({error: ex}));
            }
        };
        
        // Use api call to get amount of listings for the specified filters
        listingsTotal = await getTotalListingCount();
        if (debugOutput) console.log(`Total Listings: ${listingsTotal}`);

        // Pages at 100 item per to fetch
        console.log(Math.floor(listingsTotal / listingsPerPage));
        let idRange = [...Array(Math.floor(listingsTotal / listingsPerPage)).keys()];
        if (debugOutput) console.log(`Listing Pages at ${listingsPerPage} per: ${idRange.length}`);

        // Last page with X items, remainder
        let idRangeRem = [idRange.length]
        if (debugOutput) console.log(`Remaining Listings on last page: ${listingsTotal - idRange}`);
        if (debugOutput) console.log(`Fetching Listing Ids...`);

        // Concurrently fetch 'idRange' pages of ids, at 'listingsPerPage' per page using 'threads' items per subset
        listingIds = (await parallel([... idRange], fetchIds, ((o) => o.results.map(l => l.id).flat()), threads)).flat();
        if (listingsTotal - idRange !== 0) {
            if (debugOutput) console.log(`Fetching Rem Listing Ids...`);
            // Concurrently fetch 1 page of ids, at 'listingsPerPage' per page using 'listingsTotal - idRange' items per subset
            listingIds.push(... (await parallel([... idRangeRem], fetchIds, ((o) => o.results.map(l => l.id).flat()), 1)).flat());
        }
        if (debugOutput) console.log(`Fetching Listing Details By Id...`);

        // Using ids, concurrently fetch the details for each
        listingDetails = await parallel(listingIds, fetchDetails, (o) => o, threads);
        if (debugOutput) console.log(`Returning Array of Listing Details`);
        return listingDetails;
    }

    // Execute and return the result
    cb(await getData());

}());