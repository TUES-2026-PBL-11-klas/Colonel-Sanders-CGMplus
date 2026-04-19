import { useState, useCallback, useEffect } from 'react';
import { API } from '../utils/api';

export interface LoyaltyProfile {
  balance: number;
  rank: string;
}

export interface LoyaltyCard {
  nfc_id: string;
  active: boolean;
  disabled: boolean;
  expiry_date: string;
}

export interface LoyaltyOffer {
  id: number;
  name: string;
  description?: string;
  price: number;
}

export interface RedemptionHistory {
  id: string;
  offer_id: number;
  profile_id: string;
  points_cost: number;
}

export function useWalletData() {
  const [profile, setProfile] = useState<LoyaltyProfile | null>(null);
  const [card, setCard] = useState<LoyaltyCard | null>(null);
  const [offers, setOffers] = useState<LoyaltyOffer[]>([]);
  const [redemptions, setRedemptions] = useState<RedemptionHistory[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchWalletData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const results = await Promise.allSettled([
        API.getProfileSummary(),
        API.getCardDetails(),
        API.getActiveOffers(),
        API.getRedemptionHistory()
      ]);

      const [profileRes, cardRes, offersRes, redemptionsRes] = results;

      if (profileRes.status === 'fulfilled' && profileRes.value.ok) {
        setProfile(await profileRes.value.json());
      } else {
        console.warn('Failed to fetch profile summary');
      }

      if (cardRes.status === 'fulfilled' && cardRes.value.ok) {
        setCard(await cardRes.value.json());
      } else {
        console.warn('Failed to fetch card details');
      }

      if (offersRes.status === 'fulfilled' && offersRes.value.ok) {
        setOffers(await offersRes.value.json());
      } else {
        console.warn('Failed to fetch active offers');
      }

      if (redemptionsRes.status === 'fulfilled' && redemptionsRes.value.ok) {
        setRedemptions(await redemptionsRes.value.json());
      } else {
        console.warn('Failed to fetch redemption history');
      }
      
    } catch (err) {
      console.error('Error fetching wallet data:', err);
      setError('An error occurred while loading your wallet data.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchWalletData();
  }, [fetchWalletData]);

  return {
    profile,
    card,
    offers,
    redemptions,
    loading,
    error,
    refresh: fetchWalletData,
  };
}
