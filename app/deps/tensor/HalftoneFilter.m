//
//  Filter.m
//  PlotDevice
//
//  Created by fish2k on 12/13/13.
//
//

#import "HalftoneFilter.h"

@implementation HalftoneFilter

@synthesize filter;

- (id)init {
    self = [super init];
    if (self) {
        filter = [GPUImageHalftoneFilter init];
    }
    return self;
}

- (NSImage *)process:(NSImage *)input {
    return [filter imageByFilteringImage:input];
}

@end