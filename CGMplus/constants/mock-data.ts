export type MembershipCardMock = {
  holderName: string;
  expiry: string;
  cardNumber: string;
  accentColor: string;
};

export const membershipCardMock: MembershipCardMock = {
  holderName: 'KALOYAN YANEV',
  expiry: '11/29',
  cardNumber: '4827 1703 9136 2841',
  accentColor: '#1d5448',
};

export type Ticket = {
  id: string;
  type: 'Bus' | 'Tram' | 'Trolley' | 'Metro';
  title: string;
  status: 'Active' | 'Expired' | 'Used';
  expiry: string;
};

export const MOCK_TICKETS: Ticket[] = [
  {
    id: '1',
    type: 'Bus',
    title: 'Night Transport Pass',
    status: 'Active',
    expiry: '8.04.2026',
  },
  {
    id: '2',
    type: 'Bus',
    title: '60+ Card',
    status: 'Active',
    expiry: '8.04.2026',
  },
  {
    id: '3',
    type: 'Bus',
    title: 'Line 84 Single Ride',
    status: 'Expired',
    expiry: '10.03.2026',
  },
  {
    id: '4',
    type: 'Metro',
    title: 'Metropolitan Pass',
    status: 'Expired',
    expiry: '12.02.2026',
  },
];

export type CardData = {
  type: string;
  number: string;
  holder: string;
  expiry: string;
};

export const MOCK_CARD: CardData = {
  type: 'CGM+ Premium',
  number: '4827 1703 9136 2841',
  holder: 'KALOYAN YANEV',
  expiry: '5.27.2026',
};

export type LoyaltyHistoryItem = {
  id: string;
  desc: string;
  date: string;
  pts: number;
};

export type LoyaltyData = {
  points: number;
  tier: string;
  nextTier: string;
  nextTierAt: number;
  history: LoyaltyHistoryItem[];
};

export const MOCK_LOYALTY: LoyaltyData = {
  points: 375,
  tier: 'Gold',
  nextTier: 'Platinum',
  nextTierAt: 5000,
  history: [
    {
      id: '1',
      desc: 'Metropolitan Pass',
      date: '12.02.2026',
      pts: 50,
    },
    {
      id: '2',
      desc: 'Loyalty Bonus',
      date: '5.03.2026',
      pts: 200,
    },
    {
      id: '3',
      desc: 'Line 84 Single Ride',
      date: '10.03.2026',
      pts: 50,
    },
    {
      id: '4',
      desc: '60+ Card',
      date: '7.04.2026',
      pts: 75,
    },
    {
      id: '5',
      desc: 'Night Transport Pass Redemption',
      date: '7.04.2026',
      pts: -1000,
    }
  ],
};
