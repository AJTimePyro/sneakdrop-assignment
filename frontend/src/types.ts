export interface ActiveHold {
  hold_id: number;
  sneaker_id: number;
  pair_number: number;
  expires_at: string;
  remaining_seconds: number;
  payment_id: number | null;
  payment_status: "PENDING" | "SUCCEEDED" | "FAILED" | null;
}

export interface DropStatus {
  ok: boolean;
  pairs_left: number;
  available_pairs: number;
  held_pairs: number;
  sold_pairs: number;
  total_pairs: number;
  waitlist_count: number;
  user_id: string | null;
  purchased_count: number;
  active_hold: ActiveHold | null;
  waitlist_position: number | null;
  can_buy: boolean;
}
