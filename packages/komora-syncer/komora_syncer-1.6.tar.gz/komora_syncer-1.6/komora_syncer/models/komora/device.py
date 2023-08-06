class Device():
    def __init__(self, name, description, primaryIP4Id, primaryIP4Address, serialNumber, locationId, locationName, siteId, siteName, organizationId, organizationName, rackId, rackFace, id, netBoxId, validFrom, validTo, isActive):
        self.name = name
        self.description = description
        self.primaryIP4Id = primaryIP4Id
        self.primaryIP4Address = primaryIP4Address
        self.serialNumber = serialNumber
        self.locationId = locationId
        self.locationName = locationName
        self.siteId = siteId
        self.siteName = siteName
        self.organizationId = organizationId
        self.organizationName = organizationName
        self.rackId = rackId
        self.rackFace = rackFace
        self.validFrom = validFrom
        self.validTo = validTo
        self.isActive = isActive
        self.id = id

        self.netBoxId = netBoxId

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
