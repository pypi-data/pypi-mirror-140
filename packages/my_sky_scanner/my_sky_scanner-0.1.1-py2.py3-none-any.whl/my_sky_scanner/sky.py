"""
~~~~~~~~~~~~

This module implements the MySkyScanner API.

:copyright: no copyright
:license: MIT, see LICENSE for more details.

"""


import requests, json, pytz
from datetime import datetime

booking_api_url = "https://www.ryanair.com/api/booking/v4/en-gb/availability"

# today_date = datetime.now(pytz.timezone('Europe/Rome')).strftime("%Y/%m/%d")


class Trip:
    """
    A class used to represent a Trip

    Attributes
    ----------
        ADT (:obj:`int`, optional)
            Number of adults (age >= 16)

        TEEN (:obj:`int`, optional)
            Number of teens (12 <= age <= 15)

        CHD (:obj:`int`, optional)
            Number of children (2 <= age <= 11)

        INF (:obj:`int`, optional)
            Number of infants (age <= 2)

        DateIn (:obj:`string`, optional)
            Return flight date, blank means no return flight
            format -> "yyyy-mm-dd"

        DateOut (:obj:`string`)
            Departure flight date
            format -> "yyyy-mm-dd"

        Destination (:obj:`string`)
            The iata code of the destination airport

        Origin (:obj:`string`)
            The iata code of the origin airport

        IncludeConnectingFlights (:obj:`string` 'true'|'false')
            if false only looks for fast-track, otherwise looks for indirect flights

        FlexDaysBeforeIn (:obj:`int`, optional, range [0,3])
            Specify how flexible is your return date (before)
            example: if FlexDaysBeforeIn=3 and DateIn='2010-10-25' you will receive flights infos of 24, 23 and 22 October 2010

        FlexDaysIn  (:obj:`int`, optional, range [0,3])
            Specify how flexible is your return date (after)
            example: if FlexDaysIn=3 and DateIn='2010-10-25' you will receive flights infos of 26, 27 and 28 October 2010

        RoundTrip (:obj:`string` 'true'|'false')
            it must be set to true if want to get return flights info, false otherwise

        FlexDaysBeforeOut (:obj:`int`, optional, range [0,3])
            Specify how flexible is your departure date (before)
            example: if FlexDaysBeforeOut=3 and DateOut='2010-10-20' you will receive flights infos of 19, 18 and 17 October 2010

        FlexDaysOut (:obj:`int`, optional, range [0,3])
            Specify how flexible is your departure date (after)
            example: if FlexDaysOut=3 and DateOut='2010-10-20' you will receive flights infos of 21-22-23 October 2010

    Methods
    -------
    says(sound=None)
        Prints the animals name and what sound it makes
    """

    def __init__(
        self,
        adults,
        teens=None,
        children=None,
        infants=None,
        dateOut=None,
        dateIn=None,
        origin=None,
        destination=None,
        includeConnectingFlights=None,
        flexDaysBeforeIn=None,
        flexDaysIn=None,
        roundTrip=None,
        flexDaysBeforeOut=None,
        flexDaysOut=None,
        toUs=None,
    ) -> None:
        self._adults = adults or 1
        self._teens = teens or 0
        self._children = children or 0
        self._infants = infants or 0
        self._dateOut = dateOut or ""
        self._dateIn = dateIn or ""
        self._origin = origin or ""
        self._destination = destination or ""
        self._includeConnectingFlights = includeConnectingFlights or "false"
        self._flexDaysBeforeIn = flexDaysBeforeIn or 2
        self._flexDaysIn = flexDaysIn or 2
        self._roundTrip = roundTrip or "false"
        self._flexDaysBeforeOut = flexDaysBeforeOut or 2
        self._flexDaysOut = flexDaysOut or 2
        self._toUs = toUs or "AGREED"

    @property
    def adults(self):
        return self._adults

    @adults.setter
    def adults(self, how_many_adt):
        if how_many_adt < 0:
            raise ValueError("Can't search a trip for a negative number of person")
        self._adults = how_many_adt

    @property
    def teens(self):
        return self._teens

    @teens.setter
    def teens(self, how_many_teen):
        if how_many_teen < 0:
            raise ValueError("Can't search a trip for a negative number of person")
        self._teens = how_many_teen

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, how_many_chd):
        if how_many_chd < 0:
            raise ValueError("Can't search a trip for a negative number of children")
        self._children = how_many_chd

    @property
    def infants(self):
        return self._infants

    @infants.setter
    def infants(self, how_many_inf):
        if how_many_inf < 0:
            raise ValueError("Can't search a trip for a negative number of person")
        self._infants = how_many_inf

    @property
    def dateOut(self):
        return self._dateOut

    @dateOut.setter
    def dateOut(self, dateOut):

        format = "%Y-%m-%d"
        try:
            if bool(datetime.strptime(dateOut, format)):
                self._dateOut = dateOut
        except ValueError:
            raise ValueError("The date you inserted is not valid, format requested 'YYYY-MM-DD' ")

    @property
    def dateIn(self):
        return self._dateIn

    @dateIn.setter
    def dateIn(self, dateIn):

        format = "%Y-%m-%d"
        try:
            if bool(datetime.strptime(dateIn, format)):
                self._dateOut = dateIn
        except ValueError:
            raise ValueError("The date you inserted is not valid, format requested 'YYYY-MM-DD' ")

    @property
    def origin(self):
        return self._origin

    @origin.setter
    def origin(self, origin):
        self._origin = origin

    @property
    def destination(self):
        return self._destination

    @destination.setter
    def destination(self, destination):
        self._destination = destination

    @property
    def includeConnectingFlights(self):
        return self._includeConnectingFlights

    @includeConnectingFlights.setter
    def flexDaysBeforeIn(self, includeConnectingFlights):
        self._includeConnectingFlights = includeConnectingFlights

    @property
    def flexDaysBeforeIn(self):
        return self._flexDaysBeforeIn

    @flexDaysBeforeIn.setter
    def flexDaysBeforeIn(self, flexDaysBeforeIn):
        self._flexDaysBeforeIn = flexDaysBeforeIn

    @property
    def flexDaysIn(self):
        return self._flexDaysIn

    @flexDaysIn.setter
    def flexDaysIn(self, flexDaysIn):
        self._flexDaysIn = flexDaysIn

    @property
    def roundTrip(self):
        return self._roundTrip

    @roundTrip.setter
    def flexDaysBeforeOut(self, roundTrip):
        self._roundTrip = roundTrip

    @property
    def flexDaysBeforeOut(self):
        return self._flexDaysBeforeOut

    @flexDaysBeforeOut.setter
    def flexDaysBeforeOut(self, flexDaysBeforeOut):
        self._flexDaysBeforeOut = flexDaysBeforeOut

    @property
    def flexDaysOut(self):
        return self._flexDaysOut

    @flexDaysOut.setter
    def flexDaysOut(self, flexDaysOut):
        self._flexDaysOut = flexDaysOut

    @property
    def toUs(self):
        return self._toUs

    @toUs.setter
    def toUs(self, toUs):
        self._toUs = toUs

    def toString(self):
        return (
            "Trip info\n"
            + "Origin: "
            + self.origin
            + "\nDestination: "
            + self.destination
            + "\nAdults: "
            + str(self.adults)
            + "\nChildren: "
            + str(self.children)
            + "\nDeparture date: "
            + self.dateOut
            + "\nReturn date: "
            + self.dateIn
        )

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


def example_call():

    params = dict(
        ADT=2,  # numero di passeggeri ADULTI
        CHD=0,  # numero di passeggeri BAMBINI
        DateIn="",  # !! DATA VOLO RITORNO !! Se non specificato, il volo si intende automaticamente di sola andata
        DateOut="2022-6-20",  # !! DATA VOLO ANDATA !!
        Destination="MXP",  # AEROPORTO DESTINAZIONE
        Disc=0,  # !! UNKNOWN
        INF=0,  # !! UNKNOWN
        Origin="SUF",  # AEROPORTO ORIGINE
        TEEN=0,
        promoCode="",  # PROMO CODE
        IncludeConnectingFlights="false",  # SPECIFY THE ROUTE
        FlexDaysBeforeIn=2,  # Same as 'FlexDaysBeforeOut'
        FlexDaysIn=2,  # Same as 'FlexDaysOut'
        RoundTrip="true",
        FlexDaysBeforeOut=2,  # INDICA IL NUMERO DI QUANTI GIORNI PRIMA SI VUOLE RICEVERE INFORMAZIONI
        #
        #   [0,3]
        #   ES: Se la data di partenza indicata è il 10 marzo settando '3' si riceveranno informazioni dei voli fino a 3 gg prima
        #
        FlexDaysOut=2,  # INDICA IL NUMERO DI QUANTI GIORNI DOPO SI VUOLE RICEVERE INFORMAZIONI
        #
        #    [0,3]
        #   ES: Se la data di partenza indicata è il 10 marzo settando '2' si riceveranno informazioni dei voli fino a 2 gg dopo
        #
        ToUs="AGREED",  # !! UNKNOWN
    )

    resp = requests.get(url=booking_api_url, params=params)
    data = resp.json()

    # dati voli andata
    outTrip = data["trips"][0]  # dati del viaggio
    outTripDates = outTrip["dates"]  # ritorna un array con le date dei voli

    for date in outTripDates:
        print(date["dateOut"])  # la data relativa ai voli
        flights = date["flights"]  # lista dei voli disponibili per quella data

        for flight in flights:
            print(flight["flightKey"])  # stringa volo
            print(flight["operatedBy"])  # da chi viene operato il volo
            print(flight["flightNumber"])  # numero volo
            print(flight["duration"])  # durata del volo

            # timeUTC = flight["timeUTC"]
            # print(timeUTC[0])  # orario di partenza
            # print(timeUTC[1])  # orario d'arrivo

            fares = flight["regularFare"]["fares"]  # lista tariffe

            for fare in fares:
                print(fare["amount"])  # costo della tariffa
                print(fare["count"])  # numero di posti a tale prezzo
                # fare["hasDiscount"] # indica se scontato o no
                # fare["publishedFare"] # tariffa pubblicata (?)
                # fare["hasPromoDiscount"] # indica se ci sono delle promozioni attive su tale tariffa

    # dati voli ritorno
    if len(data["trips"]) > 1:
        inTrip = data["trips"][1]
        inTripDates = inTrip["dates"]  # ritorna un array con le date dei voli
    else:
        inTripDates = []

    for date in inTripDates:
        print(date["dateOut"])  # la data relativa ai voli
        flights = date["flights"]  # lista dei voli disponibili per quella data

        for flight in flights:
            print(flight["faresLeft"])  # nr di posti ADT rimanenti  (-1 significa indefiniti)
            print(flight["flightKey"])  # stringa volo
            print(flight["operatedBy"])  # da chi viene operato il volo
            print(flight["flightNumber"])  # numero volo
            print(flight["duration"])  # durata del volo

            # timeUTC = flight["timeUTC"]
            # print(timeUTC[0])  # orario di partenza
            # print(timeUTC[1])  # orario d'arrivo

            fares = flight["regularFare"]["fares"]  # lista tariffe

            for fare in fares:
                print(fare["amount"])  # costo della tariffa
                print(fare["count"])  # numero di posti a tale prezzo
                # fare["hasDiscount"] # indica se scontato o no
                # fare["publishedFare"] # tariffa pubblicata (?)
                # fare["hasPromoDiscount"] # indica se ci sono delle promozioni attive su tale tariffa


def get_raynair_info(trip: Trip):
    """
    Return a json containings all the informations for the trip given as parameter

    Parameters
    ----------
    trip (:obj:`Trip`)
        The trip with all the informations needed to make the api call

    Return
    ------
    (:obj:`json`)
        json containings all the informations for the given trip

    Raises
    ------
    SomeError
        BLABLABLABLA.

    """

    params = dict(
        ADT=trip.adults,
        CHD=trip.children,
        DateIn=trip.dateIn,
        DateOut=trip.dateOut,
        Destination=trip.destination,
        Origin=trip.origin,
        TEEN=trip.teens,
        IncludeConnectingFlights=trip.includeConnectingFlights,
        FlexDaysBeforeIn=trip.flexDaysBeforeIn,
        FlexDaysIn=trip.flexDaysIn,
        RoundTrip=trip.roundTrip,
        FlexDaysBeforeOut=trip.flexDaysBeforeOut,
        FlexDaysOut=trip.flexDaysOut,
        ToUs=trip.toUs,
    )

    resp = requests.get(url=booking_api_url, params=params)
    data = resp.json()

    return data
