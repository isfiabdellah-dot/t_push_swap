/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   bench.c                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: aisfi <marvin@42.fr>                       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/28 17:40:28 by aisfi             #+#    #+#             */
/*   Updated: 2026/11/28 19:03:28 by aisfi            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "../header/push_swap.h"

void	bench(t_ctr *s)
{
	s->total_ops = s->sa + s->sb + s->ss + s->pa + s->pb + s->ra + s->rb;
	s->total_ops = s->total_ops + s->rr + s->rra + s->rrb + s->rrr;
	fprintf(stderr,"[bench] disorder: %f%%\n", s->disorder * 100);
	fprintf(stderr,"[bench] strategy: %s\n", s->strategy);
	fprintf(stderr,"[bench] total_ops: %d\n", s->total_ops);
	fprintf(stderr,"[bench] sa:  %d  sb:  %d  ss:  %d  pa:  %d  pb:  %d\n", s->sa, s->sb, s->ss, s->pa, s->pb);
	fprintf(stderr,"[bench] ra:  %d  rb:  %d  rr:  %d  rra:  %d  rrb:  %d  rrr: %d \n", s->ra, s->rb, s->rr, s->rra, s->rrb, s->rrr);
}
