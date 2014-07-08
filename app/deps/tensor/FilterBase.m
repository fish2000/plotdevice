//
//  FilterBase.m
//  PlotDevice
//
//  Created by fish2k on 12/13/13.
//
//

#import "FilterBase.h"

@implementation FilterBase

@synthesize filter;

- (id)init {
    self = [super init];
    if (!self) {
        return nil;
    }
    return self;
}

- (NSImage *)process:(NSImage *)input {
    return [filter imageByFilteringImage:input];
}

@end